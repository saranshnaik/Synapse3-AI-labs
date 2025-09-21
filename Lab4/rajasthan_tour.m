% ---------------------------------------------------------
% Author : Synapse^3
% Date: 20/09/2025
% CS308 AI - Simulated Annealing Example
% Rajasthan Tourism
% ---------------------------------------------------------

clear all;
close all;
rng(100);

% Rajasthan city coordinates (approximate latitude/longitude)
cities = {
    'Jaipur', 26.9124, 75.7873;
    'Udaipur', 24.5854, 73.7125;
    'Jodhpur', 26.2389, 73.0243;
    'Jaisalmer', 26.9157, 70.9083;
    'Pushkar', 26.4902, 74.5509;
    'Ajmer', 26.4499, 74.6399;
    'Mount Abu', 24.5925, 72.7156;
    'Bikaner', 28.0229, 73.3119;
    'Chittorgarh', 24.8887, 74.6269;
    'Ranthambore', 25.9929, 76.4544;
    'Bharatpur', 27.2153, 77.4928;
    'Alwar', 27.5535, 76.6346;
    'Kota', 25.2138, 75.8648;
    'Bundi', 25.4415, 75.6444;
    'Sawai Madhopur', 26.0273, 76.3475;
    'Nagaur', 27.1962, 73.7339;
    'Shekhawati', 28.1262, 75.3975;
    'Banswara', 23.5465, 74.4339;
    'Dungarpur', 23.8431, 73.7147;
    'Pali', 25.7713, 73.3233
};

N = size(cities, 1);

% Create distance matrix (approximate road distances in km)
D = zeros(N, N);
for i = 1:N-1
    for j = i+1:N
        % Calculate great circle distance (approximation)
        lat1 = cities{i, 2};
        lon1 = cities{i, 3};
        lat2 = cities{j, 2};
        lon2 = cities{j, 3};
        
        % Haversine formula for distance calculation
        R = 6371; % Earth's radius in km
        dLat = deg2rad(lat2 - lat1);
        dLon = deg2rad(lon2 - lon1);
        a = sin(dLat/2)^2 + cos(deg2rad(lat1)) * cos(deg2rad(lat2)) * sin(dLon/2)^2;
        c = 2 * atan2(sqrt(a), sqrt(1-a));
        distance = R * c;
        
        D(i, j) = distance;
        D(j, i) = distance;
    end
end

% Simulated Annealing parameters
s = randperm(N); % Initial solution
sinit = s;
ds = path_cost_tour(s, D); 
d = ds; 
Tm = 10000; % Initial temperature
iter_max = 100000;
cooling_rate = 0.9995;

fprintf('\nStarting Simulated Annealing for Rajasthan Tour...\n');
fprintf('Initial tour cost: %.2f km\n', ds);

% Progress tracking
best_cost = inf;
best_tour = s;
acceptance_rates = [];

for i = 1:iter_max
    % Generate neighbor by reversing a random segment
    id = randperm(N, 2);
    id = sort(id);
    snext = s;
    snext(id(1):id(2)) = s(id(2):-1:id(1));
    
    dsnext = path_cost_tour(snext, D);
    E = ds - dsnext; % Energy difference
    
    % Cooling schedule
    T = Tm * cooling_rate^i;
    
    accepted = false;
    
    if E > 0 
        % Always accept better solutions
        s = snext;
        ds = dsnext;
        accepted = true;
    else
        % Accept worse solutions with probability
        pE = exp(E / T);
        if rand < pE 
            s = snext;
            ds = dsnext;
            accepted = true;
        end
    end
    
    % Track acceptance rate
    acceptance_rates = [acceptance_rates, accepted];
    
    % Track best solution
    if ds < best_cost
        best_cost = ds;
        best_tour = s;
    end
    
    d = [d, ds];
    
    % Display progress
    if mod(i, 10000) == 0
        % Calculate recent acceptance rate
        recent_acceptance = mean(acceptance_rates(max(1, end-9999):end));
        fprintf('Iteration %d: Cost = %.2f km, Best = %.2f km, Accept Rate = %.2f\n', ...
                i, ds, best_cost, recent_acceptance);
    end
end

% Display final results
fprintf('\n=== OPTIMAL RAJASTHAN TOUR FOUND ===\n');
fprintf('Total distance: %.2f km\n', best_cost);
fprintf('\nTour Sequence:\n');
for i = 1:N
    fprintf('%d. %s\n', i, cities{best_tour(i), 1});
end
fprintf('%d. %s (return to start)\n', N+1, cities{best_tour(1), 1});

% Calculate approximate travel time (assuming average speed of 60 km/h)
travel_hours = best_cost / 60;
fprintf('\nEstimated travel time: %.1f hours (%.1f days at 8 hours/day)\n', ...
        travel_hours, travel_hours/8);

% Plot results with enhanced visualization
figure('Position', [100, 100, 1400, 600]);

% Plot tour map with all points labeled
subplot(1, 2, 1);
hold on;
grid on;
title('Rajasthan Tourist Circuit - Optimal Tour', 'FontSize', 14, 'FontWeight', 'bold');

% Plot cities with different colors and markers
lons = cell2mat(cities(:,3));
lats = cell2mat(cities(:,2));

% Create a color palette for different cities
colors = lines(N);
marker_size = 100;

% Plot each city with unique color and label
for i = 1:N
    scatter(lons(i), lats(i), marker_size, colors(i,:), 'filled', 'MarkerEdgeColor', 'k', 'LineWidth', 1.5);
    
    % Add labels with offset to avoid overlap
    offset_x = 0.15;
    offset_y = 0.15;
    
    % Adjust offsets for specific cities to avoid label overlap
    if ismember(i, [3, 6, 15]) % Jodhpur, Ajmer, Sawai Madhopur
        offset_x = -0.2;
    elseif ismember(i, [4, 8, 16]) % Jaisalmer, Bikaner, Nagaur
        offset_y = -0.2;
    end
    
    text(lons(i) + offset_x, lats(i) + offset_y, cities{i,1}, ...
        'FontSize', 9, 'FontWeight', 'bold', 'Color', colors(i,:), ...
        'BackgroundColor', [1 1 1 0.7], 'EdgeColor', colors(i,:), ...
        'Margin', 1);
end

% Plot tour path with arrow indicators
tour_lons = lons([best_tour, best_tour(1)]);
tour_lats = lats([best_tour, best_tour(1)]);

% Create a smooth curve for the tour path
plot(tour_lons, tour_lats, 'k-', 'LineWidth', 2.5, 'Color', [0.2 0.2 0.8]);
plot(tour_lons, tour_lats, 'w--', 'LineWidth', 1);

% Add arrows to show direction
for i = 1:length(tour_lons)-1
    mid_x = (tour_lons(i) + tour_lons(i+1)) / 2;
    mid_y = (tour_lats(i) + tour_lats(i+1)) / 2;
    
    % Calculate arrow direction
    dx = tour_lons(i+1) - tour_lons(i);
    dy = tour_lats(i+1) - tour_lats(i);
    
    % Normalize and scale arrow
    arrow_length = 0.15;
    dx = dx * arrow_length / sqrt(dx^2 + dy^2);
    dy = dy * arrow_length / sqrt(dx^2 + dy^2);
    
    % Plot arrow
    quiver(mid_x, mid_y, dx, dy, 0, 'MaxHeadSize', 2, 'Color', 'red', 'LineWidth', 2);
end

xlabel('Longitude', 'FontWeight', 'bold');
ylabel('Latitude', 'FontWeight', 'bold');
axis equal;
box on;

% Add start/end marker
plot(lons(best_tour(1)), lats(best_tour(1)), 'pentagram', ...
    'MarkerSize', 15, 'MarkerFaceColor', 'green', 'MarkerEdgeColor', 'black', 'LineWidth', 2);
text(lons(best_tour(1)) + 0.1, lats(best_tour(1)) + 0.1, 'START/END', ...
    'FontSize', 10, 'FontWeight', 'bold', 'Color', 'green', ...
    'BackgroundColor', [1 1 1 0.8]);

% Plot convergence with enhanced styling
subplot(1, 2, 2);
plot(d, 'LineWidth', 2.5, 'Color', [0.8 0.2 0.2]);
title('Convergence of Tour Cost', 'FontSize', 14, 'FontWeight', 'bold');
xlabel('Iteration', 'FontWeight', 'bold');
ylabel('Tour Distance (km)', 'FontWeight', 'bold');
grid on;
set(gca, 'GridAlpha', 0.3);

% Add final cost annotation
final_cost = best_cost;%/1000;
annotation('textbox', [0.7, 0.2, 0.2, 0.1], 'String', ...
    sprintf('Final Cost: %.2f km', final_cost), ...
    'FitBoxToText', 'on', 'BackgroundColor', [1 1 1 0.8], ...
    'EdgeColor', 'blue', 'FontWeight', 'bold');

% Helper function for path cost calculation
function cost = path_cost_tour(tour, D)
    cost = 0;
    n = length(tour);
    for i = 1:n-1
        cost = cost + D(tour(i), tour(i+1));
    end
    cost = cost + D(tour(n), tour(1)); % Return to start
end