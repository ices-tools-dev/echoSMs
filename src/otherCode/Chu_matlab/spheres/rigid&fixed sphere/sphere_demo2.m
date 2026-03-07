%% demo program to compute backscattering form function and Target strength of a rigid&fixed sphere

clear

[p, ~, ~] = fileparts(mfilename('fullpath'));
addpath(fullfile(p, '../functions'))

a=0.25;
out_flag=2;				% complex form function
scale=1;				% linear spacing in ka
proc_flag=1;			% form function vs ka
n=200;					% number of computation points 
theta=180;				% backscattering

x0=1;					% starting ka value
xe=30;					    % end ka value
para_rgd=[n x0 xe theta round(xe)+20];
[ka, fm]=rgd_sft_fs(proc_flag,1,scale,out_flag,para_rgd);

figure(1)
plot(ka,real(fm), '.-', ka, imag(fm), 'o-r',  ka, abs(fm), '.-g', 'linewidth',1.5)
xlabel('ka')
ylabel('Form Function f_m')
legend('Re(f_m)', 'Im(f_m)', '|f_m|', 'location', 'northeast')
grid on

figure(2)
TS=20*log10(abs(fm)) + 20*log10(a/2);
plot(ka,TS,'linewidth',1.5)
hold on
plot(ka, -18.08*ones(size(ka)),'-r', 'linewidth',2)
hold off
xlabel('ka', 'fontsize', 20)
ylabel('TS (dB)', 'fontsize', 20)
grid on

