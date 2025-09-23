# plag_alignment_lev.py
import heapq
import re
import argparse
import os
import sys
import unicodedata

# PDF/Word support
try:
    from PyPDF2 import PdfReader
    _HAS_PYPDF2 = True
except:
    _HAS_PYPDF2 = False

try:
    from docx import Document
    _HAS_PYDOCX = True
except:
    _HAS_PYDOCX = False

# ---------------- file reading ----------------
def read_txt(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def read_pdf(path):
    if not _HAS_PYPDF2:
        raise ImportError("PyPDF2 not installed. pip install PyPDF2")
    reader = PdfReader(path)
    text = []
    for p in reader.pages:
        t = p.extract_text()
        if t:
            text.append(t)
    return " ".join(text).replace('\n',' ').replace('\r',' ').strip()

def read_docx(path):
    if not _HAS_PYDOCX:
        raise ImportError("python-docx not installed. pip install python-docx")
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs if p.text.strip()]
    return " ".join(paras).replace('\n',' ').replace('\r',' ').strip()

def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext=='.txt': return read_txt(path)
    if ext=='.pdf': return read_pdf(path)
    if ext=='.docx': return read_docx(path)
    raise ValueError("Unsupported file type: " + ext)

# ---------------- text processing ----------------
def sentence_tokenize(text):
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sents if s.strip()]

def normalize_sentence(s):
    s = ''.join(c for c in s if unicodedata.category(c)[0]!='C')
    s = unicodedata.normalize('NFKD', s)
    s = s.lower()
    s = re.sub(r'[-–—“”"\'.,!?;:(){}]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

# ---------------- Levenshtein distance ----------------
def levenshtein(a,b):
    la, lb = len(a), len(b)
    if la==0: return lb
    if lb==0: return la
    prev = list(range(lb+1))
    for i in range(1, la+1):
        cur = [i] + [0]*lb
        for j in range(1, lb+1):
            ins = cur[j-1]+1
            delete = prev[j]+1
            replace = prev[j-1] + (0 if a[i-1]==b[j-1] else 1)
            cur[j] = min(ins, delete, replace)
        prev = cur
    return prev[lb]

# ---------------- similarity ----------------
def similarity_label(sim):
    """sim = similarity percentage"""
    if sim >= 80: return "Exact match"
    if sim >= 60: return "Strong similarity"
    if sim >= 40: return "Moderate similarity"
    return "Low similarity"

def truncate(s, length=80):
    return s if len(s)<=length else s[:length]+'...'

# ---------------- A* alignment ----------------
def align_documents_from_text(docA_text, docB_text, skip_penalty=200):
    rawA = sentence_tokenize(docA_text)
    rawB = sentence_tokenize(docB_text)
    A = [normalize_sentence(s) for s in rawA]
    B = [normalize_sentence(s) for s in rawB]
    n,m = len(A), len(B)
    if n==0 or m==0: return None

    start=(0,0)
    goal=(n,m)
    frontier=[]
    heapq.heappush(frontier,(0,0,0,0,None,None))  # (f, g, i, j, parent, action)
    came_from={}
    gscore={(0,0):0}
    closed=set()

    while frontier:
        f,g,i,j,parent,action = heapq.heappop(frontier)
        key=(i,j)
        if key in closed: continue
        came_from[key]=(parent,action)
        if key==goal:
            # reconstruct path
            path=[]
            cur=key
            while cur!=start:
                p,act=came_from[cur]
                path.append((act,cur))
                cur=p
            path.reverse()
            return {'rawA':rawA,'rawB':rawB,'normA':A,'normB':B,'path':path,'g':g}
        closed.add(key)

        # Match
        if i<n and j<m:
            ni,nj=i+1,j+1
            cost=levenshtein(A[i],B[j])
            ng=g+cost
            if (ni,nj) not in gscore or ng<gscore[(ni,nj)]:
                gscore[(ni,nj)]=ng
                heapq.heappush(frontier,(ng,ng,ni,nj,key,('MATCH',i,j)))
        # Skip A
        if i<n:
            ni,nj=i+1,j
            ng=g+skip_penalty
            if (ni,nj) not in gscore or ng<gscore[(ni,nj)]:
                gscore[(ni,nj)]=ng
                heapq.heappush(frontier,(ng,ng,ni,nj,key,('SKIP_A',i)))
        # Skip B
        if j<m:
            ni,nj=i,j+1
            ng=g+skip_penalty
            if (ni,nj) not in gscore or ng<gscore[(ni,nj)]:
                gscore[(ni,nj)]=ng
                heapq.heappush(frontier,(ng,ng,ni,nj,key,('SKIP_B',j)))
    return None

# ---------------- pretty print ----------------
def pretty_print_alignment(res):
    if res is None:
        print("No alignment found.")
        return
    rawA,resA=res['rawA'],res['rawA']
    rawB,resB=res['rawB'],res['rawB']
    path=res['path']
    total_cost=res['g']

    print("\n=== Alignment Summary ===")
    print(f"Total alignment cost: {total_cost:.1f}")
    print(f"Document A sentences: {len(rawA)} | Document B sentences: {len(rawB)}\n")
    hdr=f"{'Action':8} | {'Index A':7} | {'Index B':7} | {'Cost':6} | {'Similarity':10} | {'Label':18} | Sentence A -> Sentence B"
    print(hdr)
    print("-"*len(hdr))

    matched_pairs=0; exact=0; strong=0; moderate=0

    for act,pos in path:
        kind=act[0]
        if kind=='MATCH':
            i,j=act[1],act[2]
            cost=levenshtein(res['normA'][i],res['normB'][j])
            sim=100 - cost/max(len(res['normA'][i]),1)*100
            label=similarity_label(sim)
            if label=="Exact match": exact+=1
            elif label=="Strong similarity": strong+=1
            elif label=="Moderate similarity": moderate+=1
            matched_pairs+=1
            print(f"{'MATCH':8} | {i:<7} | {j:<7} | {cost:<6} | {sim:6.1f}%    | {label:<18} | \"{truncate(rawA[i])}\" -> \"{truncate(rawB[j])}\"")
        elif kind=='SKIP_A':
            i=act[1]
            print(f"{'SKIP_A':8} | {i:<7} | {'-':7} | {'-':6} | {'-':10} | {'Skipped from A':<18} | \"{truncate(rawA[i])}\" -> (skipped)")
        else:
            j=act[1]
            print(f"{'SKIP_B':8} | {'-':7} | {j:<7} | {'-':6} | {'-':10} | {'Skipped from B':<18} | (skipped) -> \"{truncate(rawB[j])}\"")

    print("\n=== Quick stats ===")
    print(f"Matched sentence pairs: {matched_pairs}")
    print(f"Exact matches: {exact}")
    print(f"Strong similarities: {strong}")
    print(f"Moderate similarities: {moderate}")
    if matched_pairs>0:
        print(f"Exact match ratio: {exact/matched_pairs:.2%}")
        print(f"Strong similarity ratio: {strong/matched_pairs:.2%}")
        print(f"Moderate similarity ratio: {moderate/matched_pairs:.2%}")
    print("========================")

    # Plagiarism score
    total_sentences_A=len(rawA)
    if total_sentences_A>0:
        score_percent=(exact + strong + moderate)/total_sentences_A*100
        if score_percent>=70: level="High"
        elif score_percent>=40: level="Medium"
        else: level="Low"
        print(f"\n=== Plagiarism Score ===")
        print(f"Plagiarism coverage: {score_percent:.1f}% -> {level}")
        print("========================\n")

    print(f"=== Total Alignment Cost: {total_cost:.1f} ===\n")

# ---------------- CLI ----------------
def main():
    p=argparse.ArgumentParser(description="A* sentence-level alignment (txt,pdf,docx).")
    p.add_argument('fileA',help="Path to first document")
    p.add_argument('fileB',help="Path to second document")
    p.add_argument('--skip',type=int,default=200,help="Skip penalty (default 200)")
    args=p.parse_args()

    try:
        textA=read_file(args.fileA)
        textB=read_file(args.fileB)
    except Exception as e:
        print("Error reading files:",e)
        sys.exit(1)

    res=align_documents_from_text(textA,textB,skip_penalty=args.skip)
    pretty_print_alignment(res)

if __name__=="__main__":
    main()
