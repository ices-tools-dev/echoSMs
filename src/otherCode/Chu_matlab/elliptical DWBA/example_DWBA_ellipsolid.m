% Backscattering by a spheroid (Target Strength - TS), and the program is capable of performing non-average 
% or average over angle and/or length, and returns the averaged target strength 
% TS as a function of frequency, theta (polar angle, or dorsal aspect), phi
% (azimuth aspect)
% 
% Dezhang Chu, NOAA Fisheries, NWFSC, created on 12 Nov 2012
% modification on 12/08/2019 
% modification on 08/04/2021 updated comments (a, b, c)

clear

addpath(genpath('functions'))

%% Set parameters
%% physical properties of the scattering object
para.phy.g = 1.04;               % density contrast   
para.phy.h = 1.03;               % sound speed contrast
%% geometric shape of the object
para.shape.a=20;                 % semi-minor axis (height/2 in mm)
para.shape.b=15;                 % semi-minor axis (width/2 in mm)
para.shape.c=160;                % semi-major axis (length/2 in mm)
%% simulation parameters
para.simu.cw=1500;               % sound speed in water (m/s)
para.simu.n=1000;                % number of frequency data points
para.simu.freq0_min = 500;      % minimum output frequency in Hz
para.simu.freq0_max = 80e3;     % maximum output frequency in Hz
theta_min = -90;                 % minimum polar angle
theta_max = 90;                  % maximum polar angle
phi_min = 0;                   % minimum azimuth angle
phi_max = 180;                    % maximum azimuth angle
nth = 181;                       % number of theta values
nphi = 361;                      % number of phi values

%% average over angle of orientation (theta and phi)
para.simu.ang.ave_para(1) = 0; % mean value in deg
para.simu.ang.ave_para(2) = 10; % standard deviation in deg
para.simu.ang.ave_para(3) =100; % number of bins to be averaged over

%% average over length
para.simu.len.ave_para(1) = 1; % normalized mean length = 1
para.simu.len.ave_para(2) = 0.1; % standard deviation/mean length = CV
para.simu.len.ave_para(3) = 100; % number of bins to be averaged over

example_index = 22;               
% example index
%  1: no average: TS vs freq,  theta =0 , phi = 0 (broadside & dorsal view)
%  2: no average: TS vs theta, freq = 120 kHz, phi = 0 (dorsal view)
%  3: no average: TS vs phi,   freq = 120 kHz, theta = 0 (broadside)
%  4: no average: TS vs freq & theta (2D),  phi = 0 (dorsal view)
%  5: no average: TS vs freq & phi (2D),    theta = 0 (broadsize)
%  6: no average: TS vs theta & phi (2D),   freq = 120 kHz
%  7: average: TS vs freq, average over theta,     theta_PDF = N(0,20), phi = 0 (dorsal view)
%  8: average: TS vs freq, average over phi,       theta = 0 (broadsize), phi_PDF = N(0, 20) 
%  9: average: TS vs freq, average over length,    len_PDF = N(1,0.1), freq = 120 kHz, theta = 0 (broadside), phi = 0 (dorsal view)
% 10: average: TS vs theta, average over theta,    freq = 120 kHz, theta_PDF = N(0, 20), phi = 0 (dorsal view)
% 11: average: TS vs theta, average over phi,      freq = 120 kHz, phi_PDF = N(0, 20)
% 12: average: TS vs theta, average over length,   freq = 120 kHz, len_PDF = N(1, 0.1), phi = 0 (dorsal view)
% 13: average: TS vs phi, average over theta,      freq = 120 kHz, theta_PDF = N(0, 20)
% 14: average: TS vs phi, average over phi,        freq = 120 kHz, theta = 0 (broadsize), phi_PDF = N(0, 20)
% 15: average: TS vs phi, average over length,     freq = 120 kHz, len_PDF = N(1, 0.1), theta = 0 (broadside)
% 16: average: TS vs freq, average over theta and length,   theta_PDF = N(0, 20), len = N(1,0.1), phi = 0 (dorsal view)
% 17: average: TS vs freq, average over phi and length,     theta = 0 (broadside), phi_PDF = N(0, 20), len_PDF = N(1,0.1)
% 18: average: TS vs theta, average over theta and length,  len_PDF = N(1,0.1), theta_PDF = N(0, 20),  phi = 0 (dorsal view)
% 19: average: TS vs theta, average over theta and phi,     freq = 120 kHz, theta_PDF = N(0, 20),  phi = 0 (dorsal view)
% 20: average: TS vs phi,   average over phi and length,    freq = 120 kHz, len_PDF = N(1,0.1),  theta = 0 (broadside), phi_PDF = N(0, 20)
% 21: average: TS vs phi,   average over theta and phi,     freq = 120 kHz, theta_PDF = N(0, 20), phi_PDF = N(0, 20)
% 22: avergae: TS vs freq, average over theta, phi, and length, len_PDF = N(1,0.1), theta_PDF = N(0, 20), phi_PDF = N(0, 20)
                                 
%% parameters for averaging over orientation and length
%% para.simu.ave_flag:  Average flag: 
                             % 0: no average; 
                             % 1: average over angle
                             % 2: average over length 
                             % 3: average over both angle and length
                             % 4: average over both theta and phi
                             % 5: average over theta, phi, and length

%% para.simu.ave_angle_type: Average angle type
                            % 1: over theta (polar angle)
                            % 2: over phi (azimuth angle)
                            
%% para.simu.TS_var: TS versus variable
                            % 1: vs freq
                            % 2: vs theta (polar angle)
                            % 3: vs phi (azimuth angle)      
                            
switch example_index
    case {1, 7, 8, 9, 16, 17}
        para.simu.TS_var = 1;  % vs freq
    case {2, 10, 11, 12, 18, 19}
        para.simu.TS_var = 2;  % vs theta
    case {3, 13, 14, 15, 20, 21}
        para.simu.TS_var = 3;  % vs phi
end
                          
switch example_index
    case 1     % TS vs freq
        para.simu.ave_flag=0;            % average flag:
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.freq = para.simu.freq0;
        para.simu.theta = 0;             % angle of incidence in deg    (0 for broadside)
        para.simu.phi = 0;               % azimuth angle of incidence in deg (0 for dorsal aspect, 90 for lateral aspect)
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = 'TS (dB)';
        title_str = sprintf('\\theta = %3.1f^o,   \\phi = %3.1f^o', para.simu.theta, para.simu.phi);
    case 2     % TS vs theta
        para.simu.ave_flag=0;            % average flag:
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.freq0 = 120e3;         % frequency
        para.simu.phi=0;                 % azimuth angle of incidence in deg (0 for dorsal aspect, 90 for lateral aspect)
        xlabel_str = '\theta (deg)';
        ylabel_str = 'TS (dB)';
        title_str = sprintf('freq = %3.1f (kHz),   \\phi = %3.1f^o', para.simu.freq0*1e-3, para.simu.phi);
    case 3      % TS vs phi
        para.simu.ave_flag=0;            % average flag:
        para.simu.phi = linspace(phi_min+eps,phi_max-eps,nphi);      % azimuth angle of incidence in deg (0 for dorsal aspect, 90 for lateral aspect)
        para.simu.freq0 = 120e3;         % frequency
        para.simu.theta=0;               % azimuth angle of incidence in deg (0 for dorsal aspect, 90 for lateral aspect)
        xlabel_str = '\phi (deg)';
        ylabel_str = 'TS (dB)';
        title_str = sprintf('freq = %3.1f (kHz),   \\theta = %3.1f^o', para.simu.freq0*1e-3, para.simu.theta);
    case 4       % 2D: TS vs freq & theta
        para.simu.ave_flag=0;            % average flag:
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.freq = para.simu.freq0;
        para.simu.phi = 0;               % (0 for dorsal aspect)
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '\theta (deg)';
        title_str = sprintf('TS (dB): \\phi = %3.1f deg',para.simu.phi);
    case 5       % 2D: TS vs freq & phi
        para.simu.ave_flag=0;% average flag:
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.phi = linspace(phi_min+eps,phi_max-eps,nphi);         % azimuth angle of incidence in deg (0 for dorsal aspect, 90 for lateral aspect)
        para.simu.freq = para.simu.freq0;
        para.simu.theta=0;
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '\phi (deg)';
        title_str = sprintf('TS (dB): \\theta = %3.1f deg',para.simu.theta);
    case 6        % 2D: TS vs theta & phi
        para.simu.ave_flag = 0;           % average flag:
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(phi_min+eps,phi_max-eps,nphi);         % azimuth angle of incidence in deg (0 for dorsal aspect, 90 for lateral aspect)
        para.simu.freq0= 120e3;
        xlabel_str = '\theta (deg)';
        ylabel_str = '\phi (deg)';
        title_str = sprintf('TS (dB):  freq = %3.1f kHz',para.simu.freq0*1e-3);
    case 7        % TS vs freq, average over theta
        para.simu.ave_flag = 1;           % average flag:
        para.simu.ave_angle_type = 1;     % average over theta
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.freq = para.simu.freq0;
        para.simu.phi = 0;                % (0 for dorsal aspect)
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '<TS>_{\theta}';
        title_str = sprintf('\\phi = %3.1f^o,  PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o)', para.simu.phi, para.simu.ang.ave_para(1:2));
    case 8        % TS vs freq, average over phi
        para.simu.ave_flag = 1;           % average flag
        para.simu.ave_angle_type = 2;     % average over phi
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.phi = linspace(phi_min+eps,phi_max-eps,nphi);      % azimuth angle of incidence in deg (0 for dorsal aspect, 90 for lateral aspect)
        para.simu.freq = para.simu.freq0;
        para.simu.theta=0;                % broadside
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '<TS>_{\phi}';
        title_str = sprintf('\\theta = %3.1f^o,  PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', para.simu.theta, para.simu.ang.ave_para(1:2));
    case 9        % TS vs freq, average over length
        para.simu.ave_flag=2;            % average flag:
        para.simu.theta = 0;             % angle of incidence in deg    (0 for broadside)
        para.simu.phi = 0;               % dorsal aspect
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.freq_min=para.simu.freq0_min*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0_max*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '<TS>_{L}';
        title_str = sprintf('PDF_L = N_L(%2.1f, %2.1f), \\theta = %3.1f^o,  \\phi = %3.1f^o', ...
            para.simu.len.ave_para(1:2), para.simu.theta, para.simu.phi);
    case 10      % TS vs theta, averge over theta
        para.simu.ave_flag=1;            % average flag:        
        para.simu.ave_angle_type = 1;    % average over theta
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = 0;               % dorsal aspect
        para.simu.freq0= 120e3;
        xlabel_str = '\theta (deg)';
        ylabel_str = '<TS>_{\theta}';
        title_str = sprintf('freq = %4.0f kHz, PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o), \\phi = %3.1f^o', ...
            para.simu.freq0*1e-3, para.simu.ang.ave_para(1:2), para.simu.phi);
    case 11   % TS vs theta average over phi
        para.simu.ave_flag=1;            % average flag:
        para.simu.ave_angle_type = 2;    % average over phi
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);      % azimuth angle
        para.simu.freq0= 120e3;
        xlabel_str = '\theta (deg)';
        ylabel_str = '<TS>_{\theta}';
        title_str = sprintf('freq = %4.0f kHz, PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', ...
            para.simu.freq0*1e-3, para.simu.ang.ave_para(1:2));
    case 12   % TS vs theta average over length
        para.simu.ave_flag=2;            % average flag:
        para.simu.freq0= 120e3;
        para.simu.freq_min=para.simu.freq0*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = 0;               % dorsal aspect
        xlabel_str = '\theta (deg)';
        ylabel_str = '<TS>_L';
        title_str = sprintf('freq = %4.0f kHz, PDF_L = N_L(%2.1f, %2.1f), \\phi = %3.1f^o', ...
            para.simu.freq0*1e-3, para.simu.len.ave_para(1:2), para.simu.phi);
    case 13   % TS vs phi average over theta
        para.simu.ave_flag=1;            % average flag:
        para.simu.ave_angle_type = 1;    % average over theta
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);      % azimuth angle
        para.simu.freq0= 120e3;
        xlabel_str = '\phi (deg)';
        ylabel_str = '<TS>_{\theta}';
        title_str = sprintf('freq = %4.0f kHz, PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o)', ...
            para.simu.freq0*1e-3, para.simu.ang.ave_para(1:2));
    case 14   % TS vs phi average over phi
        para.simu.ave_flag=1;            % average flag:
        para.simu.ave_angle_type = 2;    % average over phi
        para.simu.theta = 0;    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);      % azimuth angle
        para.simu.freq0= 120e3;
        xlabel_str = '\phi (deg)';
        ylabel_str = '<TS>_{\phi}';
        title_str = sprintf('freq = %4.0f kHz, PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', ...
            para.simu.freq0*1e-3, para.simu.ang.ave_para(1:2));
    case 15   % TS vs phi average over length
        para.simu.ave_flag=2;            % average flag:        para.simu.freq0= 120e3;
        para.simu.freq0= 120e3;
        para.simu.freq_min=para.simu.freq0*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        para.simu.theta = 0;            % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);      % azimuth angle
        xlabel_str = '\phi (deg)';
        ylabel_str = '<TS>_{L}';
        title_str = sprintf('freq = %4.0f kHz, PDF_L = N_L(%2.1f, %2.1f), \\theta = %3.1f^o', ...
            para.simu.freq0*1e-3, para.simu.len.ave_para(1:2), para.simu.theta);
    case 16   % TS vs freq, average over theta and length
        para.simu.ave_flag=3;            % average flag:        para.simu.freq0= 120e3;
        para.simu.ave_angle_type = 1;    % average over theta
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = 0;               % dorsal aspect
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.freq_min=para.simu.freq0_min*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0_max*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '<TS>_{\theta, L}';
        title_str = sprintf('PDF_L = N_L(%2.1f, %2.1f), PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o),  \\phi = %3.1f^o', ...
            para.simu.len.ave_para(1:2), para.simu.ang.ave_para(1:2), para.simu.phi);
    case 17  % TS vs freq, average over phi and length
        para.simu.ave_flag=3;            % average flag:        para.simu.freq0= 120e3;
        para.simu.ave_angle_type = 2;    % average over phi
        para.simu.theta = 0;            % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);      % azimuth angle
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.freq_min=para.simu.freq0_min*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0_max*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '<TS>_{\phi, L}';
        title_str = sprintf('PDF_L = N_L(%2.1f, %2.1f),  \\theta = %3.1f^o, PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', ...
            para.simu.len.ave_para(1:2), para.simu.theta, para.simu.ang.ave_para(1:2));
    case 18  % TS vs theta, average over length and theta
        para.simu.ave_flag=3;            % average flag:        
        para.simu.ave_angle_type = 1;    % average over theta
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = 0;               % dorsal aspect
        para.simu.freq0 = 120e3;       % output frequrncy (Hz)
        para.simu.freq_min=para.simu.freq0_min*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0_max*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        xlabel_str = '\theta (deg)';
        ylabel_str = '<TS>_{\theta, L}';
        title_str = sprintf('freq = %4.0f kHz, PDF_L = N_L(%2.1f, %2.1f), PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o), \\phi = %3.1f^o', ...
            para.simu.freq0*1e-3, para.simu.len.ave_para(1:2), para.simu.ang.ave_para(1:2), para.simu.phi);
    case 19  % TS vs theta, average over phi and theta
        para.simu.ave_flag=4;            % average flag:        
        para.simu.ave_angle_type = 1;    % average over theta
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);     % azimuth angle
        para.simu.freq0 = 120e3;       % output frequrncy (Hz)
        xlabel_str = '\theta (deg)';
        ylabel_str = '<TS>_{\phi, \theta}';
        title_str = sprintf('freq = %4.0f kHz, PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o),  PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', ...
            para.simu.freq0*1e-3, para.simu.ang.ave_para(1:2), para.simu.ang.ave_para(1:2));
    case 20  % TS vs phi, average over length and phi
        para.simu.ave_flag=3;            % average flag:        
        para.simu.ave_angle_type = 2;    % average over phi
        para.simu.theta = 0;             % broadside
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);     % azimuth angle
        para.simu.freq0 = 120e3;       % output frequrncy (Hz)
        para.simu.freq_min=para.simu.freq0_min*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0_max*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        xlabel_str = '\phi (deg)';
        ylabel_str = '<TS>_{L, \phi}';
        title_str = sprintf('freq = %4.0f kHz, PDF_L = N_L(%2.1f, %2.1f), \\theta = %3.1f^o, PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', ...
            para.simu.freq0*1e-3, para.simu.len.ave_para(1:2), para.simu.theta, para.simu.ang.ave_para(1:2));
    case 21  % TS vs phi, average over theta and phi
        para.simu.ave_flag=4;            % average flag:        
        para.simu.theta = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);     % azimuth angle
        para.simu.freq0 = 120e3;       % output frequrncy (Hz)
        xlabel_str = '\phi (deg)';
        ylabel_str = '<TS>_{\theta, \phi}';
        title_str = sprintf('freq = %4.0f kHz, PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o),  PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', ...
            para.simu.freq0*1e-3, para.simu.ang.ave_para(1:2), para.simu.ang.ave_para(1:2));           
    case 22
        para.simu.ave_flag=5;            % average flag:        
        para.simu.theta0 = linspace(theta_min+eps,theta_max-eps,nth);    % angle of incidence in deg    (0 for broadside)
        para.simu.phi = linspace(theta_min+eps,theta_max-eps,nphi);     % azimuth angle
        para.simu.freq0 = linspace(para.simu.freq0_min,para.simu.freq0_max,para.simu.n);       % output frequrncy (Hz)
        para.simu.freq_min=para.simu.freq0_min*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0_max*(1+3.5*para.simu.len.ave_para(2));
        para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
        xlabel_str = 'Frequency (kHz)';
        ylabel_str = '<TS>_{\theta, L, \phi}';
        title_str = sprintf('PDF_L = N_L(%2.1f, %2.1f), PDF_{\\theta} = N_{\\theta}(%2d^o, %2d^o),  PDF_{\\phi} = N_{\\phi}(%2d^o, %2d^o)', ...
            para.simu.len.ave_para(1:2), para.simu.ang.ave_para(1:2), para.simu.ang.ave_para(1:2));                   
end
                          

if para.simu.ave_flag <= 1 | para.simu.ave_flag == 4
    para.simu.freq=para.simu.freq0;
else
    if length(para.simu.freq0) > 1
        para.simu.freq_min=para.simu.freq0_min*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0_max*(1+3.5*para.simu.len.ave_para(2));
    else
        para.simu.freq_min=para.simu.freq0*(1-3.5*para.simu.len.ave_para(2));
        para.simu.freq_max=para.simu.freq0*(1+3.5*para.simu.len.ave_para(2));
    end
    para.simu.freq=linspace(para.simu.freq_min,para.simu.freq_max,para.simu.n);       % simulation frequrncy (Hz)
end

tic
switch para.simu.ave_flag 
    case 0   % no average
        sigma_bs=basct_DWBA_ellipsoid(para);
        TS_out=10*log10(abs(sigma_bs.fun));
    case 1   % average over angle only
        sigma_bs=basct_DWBA_ellipsoid(para);
        if para.simu.ave_angle_type == 1
            sigma_ave_ang=bscat_ave([],para.simu.theta,sigma_bs.fun,1,para.simu.ang.ave_para);
        else
            sigma_ave_ang=bscat_ave([],para.simu.phi,sigma_bs.fun,1,para.simu.ang.ave_para);
        end
        TS_out=10*log10(sigma_ave_ang);
    case 2   % average over length only
        sigma_bs=basct_DWBA_ellipsoid(para);
        sigma_ave_len=bscat_ave(para.simu.freq0,para.simu.freq,sigma_bs.fun,2,para.simu.len.ave_para);
        TS_out=10*log10(sigma_ave_len);
    case 3   % average over angle and length
        sigma_bs=basct_DWBA_ellipsoid(para);
        if para.simu.TS_var == 1  % TS vs freq
            if length(para.simu.theta) > 1  % avergae over theta (polar angle - dorsal/ventral plane)
                sigma_ave_ang=bscat_ave([],para.simu.theta,sigma_bs.fun,1,para.simu.ang.ave_para);
                y_label='<TS>_{\theta, L}';
            elseif length(para.simu.phi) > 1  % avergae over phi (azimuth angle - cross-section plane)
                sigma_ave_ang=bscat_ave([],para.simu.phi,sigma_bs.fun,1,para.simu.ang.ave_para);
                y_label='<TS>_{\phi, L}';
            end
            sigma_ave_ang_len=bscat_ave(para.simu.freq0,para.simu.freq,sigma_ave_ang,2,para.simu.len.ave_para);
            TS_out=10*log10(sigma_ave_ang_len);
        elseif para.simu.TS_var >= 2 % TS vs theta or phi
            sigma_bs.fun = sigma_bs.fun';
            para.simu.ave_flag = 2; % average over length first
            sigma_ave_len=bscat_ave(para.simu.freq0,para.simu.freq,sigma_bs.fun,2,para.simu.len.ave_para);
            if length(para.simu.theta) > 1  % avergae over theta (polar angle - dorsal/ventral plane)
                sigma_ave_len_ang=bscat_ave([],para.simu.theta,sigma_ave_len,1,para.simu.ang.ave_para);
                y_label='<TS>_{L, \theta}';
            elseif length(para.simu.phi) > 1  % avergae over phi (azimuth angle - cross-section plane)
                sigma_ave_len_ang=bscat_ave([],para.simu.phi,sigma_ave_len,1,para.simu.ang.ave_para);
                y_label='<TS>_{L, \phi}';
            end  
            TS_out=10*log10(sigma_ave_len_ang);
        end
    case 4  % average over theta and phi
        if para.simu.TS_var == 2   % TS vs theta
            para.simu.ave_angle_type = 2; % be prepared for averaging over phi first
            sigma_bs=basct_DWBA_ellipsoid(para);
            sigma_ave_phi=bscat_ave([],para.simu.theta,sigma_bs.fun,1,para.simu.ang.ave_para);  % average over phi
            sigma_ave_phi_th=bscat_ave([],para.simu.theta,sigma_ave_phi,1,para.simu.ang.ave_para);  % average over theta
            TS_out=10*log10(sigma_ave_phi_th);
        else                        % TS vs phi
            tmp_ave_flag = para.simu.ave_flag;
            para.simu.ave_flag = 1;
            para.simu.ave_angle_type = 1; % be prepared for averaging over theta first
            sigma_bs=basct_DWBA_ellipsoid(para);
            sigma_ave_th=bscat_ave([],para.simu.theta,sigma_bs.fun,1,para.simu.ang.ave_para);  % average over theta
            sigma_ave_th_phi=bscat_ave([],para.simu.phi,sigma_ave_th,1,para.simu.ang.ave_para);  % average over phi
            TS_out=10*log10(sigma_ave_th_phi);
        end
    case 5  % average over thete, phi, and length        
        para.simu.ave_angle_type = 2;       % flag for average over phi first
        fprintf('Computing, please be paticent ...\n')
        for i=1:nth                         % loop through theta
            para.simu.theta = para.simu.theta0(i);
            para.simu.ave_flag = 1;
            sigma_bs=basct_DWBA_ellipsoid(para);
            sigma_ave_th=bscat_ave([],para.simu.phi,sigma_bs.fun,1,para.simu.ang.ave_para);  % average over phi
            para.simu.ave_flag = 2;
            sigma_ave_th_len(i,1:para.simu.n)=bscat_ave(para.simu.freq0,para.simu.freq,sigma_ave_th,2,para.simu.len.ave_para); % average over phi & length
        end
        para.simu.ave_angle_type = 1;       % flag for average over theta
        para.simu.theta = para.simu.theta0; % angle of incidence in deg  (0 for broadside)
        sigma_ave_th_len_phi=bscat_ave([],para.simu.theta,sigma_ave_th_len,1,para.simu.ang.ave_para);
        TS_out=10*log10(sigma_ave_th_len_phi);
end

clf
figure(1)
switch example_index
    case {1, 7, 8, 9, 16, 17, 22}   % vs frequency
        plot(para.simu.freq*1e-3,TS_out,'b','linewidth',1.5)
    case {2, 10, 11, 12, 18, 19}   % vs theta
        plot(para.simu.theta,TS_out,'b','linewidth',1.5)
    case {3,  13, 14, 15, 20, 21}   % vs phi
        plot(para.simu.phi,TS_out,'b','linewidth',1.5)  
    case 4   % vs freq and theta
        imagesc(para.simu.freq*1e-3, para.simu.theta, TS_out);colorbar
    case 5   % vs freq and phi
        imagesc(para.simu.freq*1e-3, para.simu.phi, TS_out);colorbar
    case 6   % vs theta and phi
        imagesc(para.simu.theta, para.simu.phi, TS_out);colorbar
end

if example_index < 4 | example_index > 6  % not 2D plot
    set(gca, 'ylim', [-100 -40])
end
xlabel(xlabel_str,'fontsize',18,'fontweight','bold')
ylabel(ylabel_str,'fontsize',18,'fontweight','bold')
title(title_str)
grid on
hold off
toc
