function cost = path_cost_jigsaw(s, tiles, tile_rows, tile_cols)
cost = 0;
tile_H = size(tiles{1},1);
tile_W = size(tiles{1},2);

for r = 1:tile_rows
    for c = 1:tile_cols
        id = s((r-1)*tile_cols + c);
        % right neighbor
        if c < tile_cols
            right_id = s((r-1)*tile_cols + (c+1));
            cost = cost + sum((tiles{id}(:,end) - tiles{right_id}(:,1)).^2);
        end
        % bottom neighbor
        if r < tile_rows
            bottom_id = s(r*tile_cols + c);
            cost = cost + sum((tiles{id}(end,:) - tiles{bottom_id}(1,:)).^2);
        end
    end
end
end