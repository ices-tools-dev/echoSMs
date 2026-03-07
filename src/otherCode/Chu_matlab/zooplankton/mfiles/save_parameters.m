%% read input configuation file
function				h=save_parameters(fname)
global 	para	

fid=fopen(fname,'w');
if fid < 0
   disp(sprintf('Sorry cannot open file %s',fname));
   h=-1;
   return
end
fprintf(fid,'%s\n','%% home directory');
if isempty(para.info.home_dir)
   fprintf(fid,'%s\n',pwd);
else
   fprintf(fid,'%s\n',para.info.home_dir);
end

% save shape parameters
h=findobj(gcf,'Tag','EditTextLength');

fprintf(fid,'%s\n','%% shape	parameters');
fprintf(fid,'%d\t\t%s\n',para.shape.L,'% length in mm');
h=findobj(gcf,'Tag','CheckboxProfile');
fprintf(fid,'%d\t\t%s\n',para.shape.rho_L,'% rho/L');
fprintf(fid,'%d\t\t%s\n',para.shape.L_a,'% L/a');
fprintf(fid,'%d\t\t%s\n',para.shape.order,'% tapering order');
fprintf(fid,'%d\t\t%s\n',para.shape.ave_flag,'% length average flag: 0-no average,	1-average');
fprintf(fid,'%d\t\t%s\n',para.shape.Lstd,'% relative length standard deviation (meaningless for no average)');
fprintf(fid,'%d\t\t%s\n',para.shape.dL,'% relative length increment(meaningless for no average)');

h=findobj(gcf,'Tag','CheckboxProfile');
if get(h,'Value') == 1							% load profile
  fprintf(fid,'%s\t %s\n',para.shape.prof_name,'% shape profile name (meaningless if profile is not specified)');
else
  fprintf(fid,'%s\t %s\n','-1','% shape profile name ( "-1" if profile is not specified)');
end
fprintf(fid,'%d\t\t%s\n',para.shape.axis_sm,'% number of points for axis smoothing (meaningless if profile is not specified)');
fprintf(fid,'%d\t\t%s\n',para.shape.taper_sm,'% number of points for tapering function smoothing (meaningless if profile is not specified)');

% save orientation parameters
fprintf(fid,'%s\n','%% orientation parameters');
fprintf(fid,'%d\t\t%s\n',para.orient.angm,'% mean incident angle (deg)');
fprintf(fid,'%d\t\t%s\n',para.orient.ang0,'% angle variation range - starting value (deg)');
fprintf(fid,'%d\t\t%s\n',para.orient.ang1,'% angle variation range - ending value (deg)');
fprintf(fid,'%d\t\t%s\n',para.orient.ave_flag,'% average option flag: 0-no average,	1-average');
fprintf(fid,'%d\t\t%s\n',para.orient.PDF,'% PDF flag: 1-Uniform		2-Gaussian');
fprintf(fid,'%d\t\t%s\n',para.orient.PDF_para,'% PDF parameter: half range for Uniform PDF,');
fprintf(fid,'%s\t\t%s\n','%','% standard deviation for Gaussian (deg)');
fprintf(fid,'%s\t\t%s\n','%','% (meaningless for no average)');  
fprintf(fid,'%d\t\t%s\n',para.orient.dang,'% angle increment	(meaningless for no average)');

% save physical property parameters
fprintf(fid,'%s\n','%% physical property parameters');
fprintf(fid,'%d\t\t%s\n',para.phy.g0,'% mean density contrast (g0)');
fprintf(fid,'%d\t\t%s\n',para.phy.h0,'% mean sound speed contrast (h0)');
fprintf(fid,'%d\t\t%s\n',para.phy.seg_no,'% number of body segments (1-homogeneous body)');
fprintf(fid,'%d\t\t%s\n',para.phy.g_std,'% standard deviation of g0 (meaningless for homogeneous body)');
fprintf(fid,'%d\t\t%s\n',para.phy.h_std,'% standard deviation of h0 (meaningless for homogeneous body)');
fprintf(fid,'%d\t\t%s\n',para.phy.corrL,'% correlation length as a percentage of body length L');

% save simulation parameters
fprintf(fid,'%s\n','%% simulation parameters');
fprintf(fid,'%d\t\t%s\n',para.simu.ni,'% integration	points along body axis');
fprintf(fid,'%d\t\t%s\n',para.simu.n,'% number of output points');
fprintf(fid,'%d\t\t%s\n',para.simu.out_indx,'% output variable index: 1-scatting amplitude, 2-cross section, 3-TS, 4-RTS');
fprintf(fid,'%d\t\t%s\n',para.simu.var_indx,'% variable: 1-frequency (kHz), 2-ang(deg),  3-ka');
fprintf(fid,'%d\t\t%s\n',para.simu.var0,'% start value for the variable');
fprintf(fid,'%d\t\t%s\n',para.simu.var1,'% end value for the variable');
fprintf(fid,'%d\t\t%s\n',para.simu.freq,'% frequency (kHz), enabled for avriable being angle only');

fclose(fid);
h=0;
return
