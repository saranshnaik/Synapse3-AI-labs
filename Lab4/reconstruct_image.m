function img_out = reconstruct_image(s, tiles, rows, cols, tile_size)
img_out = zeros(rows*tile_size, cols*tile_size);
count = 1;
for r = 1:rows
    for c = 1:cols
        rr = (r-1)*tile_size+1:r*tile_size;
        cc = (c-1)*tile_size+1:c*tile_size;
        img_out(rr,cc) = tiles{s(count)};
        count = count+1;
    end
end
end