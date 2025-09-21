% ---------------------------------------------------------
% Author : Synapse^3
% Date: 20/09/2025
% CS308 AI - Simulated Annealing Example
% Jigsaw Puzzle using Simulated Annealing (4x4 tiles)
% Single-tile swaps, guaranteed valid permutation
% ---------------------------------------------------------

clear all;
close all;
rng(100);

% -------- Load Octave-style scrambled_lena.mat ----------
fid = fopen('scrambled_lena.mat','r');
tline = fgetl(fid);
while tline(1)=='#'
    tline = fgetl(fid);
end
dims = sscanf(tline,'%d');
H = dims(1);
W = dims(2);
data = fscanf(fid,'%d');
fclose(fid);
img = reshape(data,H,W);

% -------- 4x4 tiles setup ----------------
tile_rows = 4;
tile_cols = 4;
tile_H = H / tile_rows;
tile_W = W / tile_cols;

tiles = {};
count = 1;
for r = 1:tile_H:H
    for c = 1:tile_W:W
        tiles{count} = double(img(r:r+tile_H-1, c:c+tile_W-1));
        count = count+1;
    end
end

N = length(tiles);       
s = randperm(N);         
sinit = s;

ds = path_cost_jigsaw(s, tiles, tile_rows, tile_cols);
best_s = s;
best_cost = ds;

Tm = 5000000;%10000000;
T = Tm;
alpha = 0.9999;
iter_max = 50000;%100000;

% --- For plotting convergence ---
cost_history = zeros(1,iter_max);
best_history = zeros(1,iter_max);
temp_history = zeros(1,iter_max);

for i = 1:iter_max
    % --- single-tile swap neighbor ---
    id = randperm(N,2);
    snext = s;
    tmp = snext(id(1));
    snext(id(1)) = snext(id(2));
    snext(id(2)) = tmp;
    
    dsnext = path_cost_jigsaw(snext, tiles, tile_rows, tile_cols);
    delta = ds - dsnext;
    
    if delta > 0
        s = snext;
        ds = dsnext;
    else
        if rand < exp(delta/T)
            s = snext;
            ds = dsnext;
        end
    end
    
    if ds < best_cost
        best_cost = ds;
        best_s = s;
    end
    
    % record stats
    cost_history(i) = ds;
    best_history(i) = best_cost;
    temp_history(i) = T;
    
    % cool down
    T = T * alpha;
end

% -------- Display results ----------------
figure;
subplot(2,2,1);
recon = zeros(H,W);
count = 1;
for r = 1:tile_H:H
    for c = 1:tile_W:W
        recon(r:r+tile_H-1, c:c+tile_W-1) = tiles{sinit(count)};
        count = count+1;
    end
end
imshow(uint8(recon));
title('Initial Scrambled');

subplot(2,2,2);
recon = zeros(H,W);
count = 1;
for r = 1:tile_H:H
    for c = 1:tile_W:W
        recon(r:r+tile_H-1, c:c+tile_W-1) = tiles{best_s(count)};
        count = count+1;
    end
end
imshow(uint8(recon));
title('Solved Puzzle');

% -------- Graphs ----------------
subplot(2,2,3);
plot(cost_history,'b'); hold on;
plot(best_history,'r','LineWidth',1.5);
xlabel('Iteration');
ylabel('Cost');
title('Cost vs Iteration');
legend('Current Cost','Best Cost');

subplot(2,2,4);
% Estimate acceptance probability as alpha^(iteration) scaled by average delta
accept_prob = exp(-linspace(1, iter_max, iter_max)/iter_max); % Example scaling
plot(accept_prob, 'm','LineWidth',1.5);
xlabel('Iteration');
ylabel('Estimated Acceptance Probability');
title('Acceptance Probability over Iterations');
grid on;
