%% read input configuation file
% and set parameters to the structure: para
function				h=load_parameters(fname);

global 	para	

fid=fopen(fname,'r');
if fid < 0
   disp(sprintf('Sorry cannot open file %s',fname));
   h=-1;
   return
end
p=fread(fid,'char');
indx=find(p == 10);

k=1;
% home directory
indx1=find(p(indx(k)+1:indx(k+1)) == 13);
para.info.home_dir=char(p(indx(k)+1:indx(k)+indx1-1))';

k=3;
%get shape parameters
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.L=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.rho_L=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.L_a=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.order=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.ave_flag=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.Lstd=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.dL=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.prof_name=char(p(indx(k)+1:indx(k)+indx1-1))';k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.axis_sm=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.shape.taper_sm=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');

k=k+2;
% get orientation parameters
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.orient.angm=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.orient.ang0=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.orient.ang1=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.orient.ave_flag=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.orient.PDF=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.orient.PDF_para=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+3;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.orient.dang=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');

k=k+2;
% get physical property parameters
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.phy.g0=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.phy.h0=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.phy.seg_no=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.phy.g_std=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.phy.h_std=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.phy.corrL=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');

k=k+2;
% get simulation parameters
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.simu.ni=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.simu.n=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.simu.out_indx=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.simu.var_indx=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.simu.var0=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.simu.var1=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');k=k+1;
indx1=find(p(indx(k)+1:indx(k+1)) == 37);
para.simu.freq=str2num(char(p(indx(k)+1:indx(k)+indx1-1))');

fclose(fid);
h=0;