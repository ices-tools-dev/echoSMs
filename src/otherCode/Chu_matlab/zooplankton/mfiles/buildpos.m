% build vectors related to postoins of the animal
% body axis is alone z-axis
% construct shape coordinates
% 
%function    [r_pos,th_tilt,dr,gamma_t,taper,x,z]=buildpos(n_int,prof_no, order,rho_L,fname,rough_axis)
function    [r_pos,th_tilt,dr,gamma_t,taper,x,z]=buildpos

global para

n_int=para.simu.ni;
order=para.shape.order;
rho_L=para.shape.rho_L;
L_a=para.shape.L_a;
disp_prof=0;

if strcmp('-1',para.shape.prof_name(1:2)) == 1		% regular shape
% uniformly bent cylinder and regularly tapered
  gamma=0.5/rho_L;
  ratio=2*rho_L;
  z=linspace(-1,1,n_int);
  taper=sqrt(1-z(:).^order);
% normalized by rho -  radius of curvature
  z=sin(gamma)*z(:);
  x=(1-sqrt(1-z.*z));
% normalized by L/2
  x=ratio*x;
  z=ratio*z;
else				% arbitrary position profile and arbitrary tapering
  pos=load(para.shape.prof_name);
  xp=pos(:,1);
  zp=pos(:,2);
  taper1=pos(:,3);
  z=linspace(min(zp)+eps,max(zp)-eps,n_int);
  x=interp1(zp,xp,z);
  taper=interp1(zp,taper1,z);
  x=x(:)-mean(x);z=z(:)-mean(z);
  dr=sqrt(diff(x).^2+diff(z).^2);
  L=sum(dr);
  x=2*x/L;z=2*z/L;							% normalized position vector
  para.shape.x=x;
  para.shape.z=z;
  para.shape.xp=xp;
  para.shape.zp=zp;
  para.shape.taper=taper1;
end

x=x(:);z=z(:);taper=reshape(taper,1,n_int);
if strcmp(para.shape.prof_name(1:2),'-1') ~= 1
  x=smooth(x,para.shape.axis_sm);
end
if disp_prof == 1
  taper0=taper;
end
if strcmp(para.shape.prof_name(1:2),'-1') ~= 1
  taper=smooth(taper,para.shape.taper_sm);
end
th_tilt=zeros(n_int,1);
r_pos=sqrt(x.*x+z.*z);
gamma_t=atan2(z,x);
dx=diff(x)+eps;dz=diff(z);
alpha_t=[atan(dz./dx) ; atan(dz(n_int-1)/dx(n_int-1))];
indx1=find(alpha_t < 0);
if length(indx1) > 0
  th_tilt(indx1)=alpha_t(indx1)+pi/2;
end
indx2=find(alpha_t >= 0);
if length(indx2) > 0
  th_tilt(indx2)=alpha_t(indx2)-pi/2;
end
dr1=sqrt(dx.*dx+dz.*dz);
dr=[dr1(1); dr1];


if disp_prof == 1
  figure(2)
  x1=x+taper(:)/L_a;
  x2=x-taper(:)/L_a;
  x10=x+taper0(:)/L_a;
  x20=x-taper0(:)/L_a;
  plot(x,z,x1,z,'r',x2,z,'r',x10,z,'g',x20,z,'g');
%  axis('equal');grid;
 % disp('press any key to cont. ..');pause
 % plot(z,taper0,z,taper,'r');
  close(2)
end
