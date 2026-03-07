function    out = generate_profile(shape, L)
%% generate_profile returns the profile of the target object 
%% INPUT:
%%       shape = shape index of the target
%%               1:  a tipical swimbladderless fish
%%               2:  a typical euphausiid
%%               3:  a prolate spheroid 
%%           L = length in mm 
%% out = [z  xm  a  b] all in mm
%%        z: a column vector with 1-mm increment along fish lengthwise axis
%%       xm: offset distance from a mean horizontal line 
%%        a: semi-minor axis of the ellipitcal cross section (dorsal aspect)
%%        b: semi-minor axis of the ellipitcal cross section (lateral aspect)
%% 
%% created by Dezhang Chu, NWFSC  12/12/2019


% shape = 1;                  % swimbladderless fish 
n = ceil(L)+1;                % 1-mm increment
switch shape
    case 1   % fish 
        load('C:\Projects\Fish_Zooplankton_Scat_models\DWBA-elliptical cross section\profiles\ID-10401-2-SWB_FB_3D_png.mat')
        load('C:\Projects\Fish_Zooplankton_Scat_models\DWBA-elliptical cross section\profiles\ID-10401-2-SWB_FB_3D_png.mat')
        z0_lat = data.FB.lat_x;
        y0_lat = data.FB.lat_y;
        z0_dor = data.FB.dor_x;
        y0_dor = data.FB.dor_y;
        znorm_lat = max(z0_lat) - min(z0_lat);
        znorm_dor = max(z0_dor) - min(z0_dor);
        %% lateral aspect
        [~, ind1] = min(z0_lat);
        [~, ind2] = max(z0_lat);
        z_lat = linspace(z0_lat(ind1), z0_lat(ind2), n);
        x_lat_low = interp1(z0_lat(ind1:ind2), y0_lat(ind1:ind2), z_lat);
        x_lat_up = interp1([z0_lat(ind1) fliplr(z0_lat(ind2:end))], [y0_lat(ind1) fliplr(y0_lat(ind2:end))], z_lat);
        %% dorsal aspect
        [~, ind1] = min(z0_dor);
        [~, ind2] = max(z0_dor);
        z_dor = linspace(z0_dor(ind1), z0_dor(ind2), n);
        x_dor_low = interp1(z0_dor(ind1:ind2), y0_dor(ind1:ind2), z_dor);
        x_dor_up = interp1([z0_dor(ind1) fliplr(z0_dor(ind2:end))], [y0_dor(ind1) fliplr(y0_dor(ind2:end))], z_dor);        
        a = (x_lat_up - x_lat_low)/2;       % semi-minor axis of the ellipitcal cross section (dorsal aspect) obtained from X-ray image of lateral view
        b = (x_dor_up - x_dor_low)/2;       % semi-minor axis of the ellipitcal cross section (lateral aspect) obtained from X-ray image of dorsal view
        xc = (x_lat_up + x_lat_low)/2;      % center line along lengthwise axis 
        xm = xc - mean(xc);                 % offset distance from a mean horizontal line  
        ratio = L/znorm_lat;
%% scale the length to the desired length from input, L, and calculate a, b, and xm based on the same scaling factor
        z = ratio*(z_lat - z_lat(1));    
        xm = ratio*xm;
        a = ratio*a;
        b = ratio*b;
    case 2   % euphausiid
        
    case 3   % ellipsoid 
        a0 = 15;     % mm
        b0 = 10;     % mm
        L0 = 300;    % mm
        c0 = L0/2;   % mm
        z = 0:L0;    % z-axis
        a = a0*sqrt(1 - ((z - c0)/c0).^2);
        b = b0*sqrt(1 - ((z - c0)/c0).^2);
        xm = zeros(1, length(z));
        ratio = L/L0;
end
figure(2)
plot(z, a + xm, '.-b', z, b, '.-r', z, xm, '.-g')
hold on
plot(z, -a + xm, '.-b', z, -b, '.-r', z, xm, '.-g')
hold off
grid
legend('a(z) + xm', 'b(z)', 'xm(z)', 'location', 'northeast')
axis equal
xlabel('Z-axis (mm) (lengthwise)', 'fontweight', 'bold')
ylabel('X & Y axes (mm)', 'fontweight', 'bold')
title('Profile in X-Z and Y-Z Planes')
out = ratio*[z(:) xm(:) a(:) b(:)];
text(0.7, 0.05, sprintf('Length Ratio = %4.2f\n', ratio), 'sc')

