% scattering amplitude by a wealy scattering uniformly bent finite 
% inhomogenous (segmented) g and h along the body
% fluid cylinder  4/27/92 notes
% study  ka (frequency) dependence using solution based on integral solution
% no restriction on incident angle: theta function  [ka0, ang, f]=DWBAscat2(fname,simu_para, shape_para,phy_para,prof_fname)
%function  [ka0, ang, f]=DWBAscat2(fname,simu_para, shape_para,phy_para,prof_fname)
function  [ka0, ang, f]=DWBAscat

global para status misc

% shape parameters
L_a=para.shape.L_a;

% simulation parameter
n=length(misc.ka);				% # of ka point
n_int=para.simu.ni;		% # of integration points

ang=misc.ang; 		% different incident angle
m=length(ang);
th=ang(:)*pi/180;

ka0=misc.ka;

	
   % construct inhomogeneous g ang h profile (physical parameters)
if get(findobj(gcf,'Tag','CheckboxInhomo'),'Value') == 0
  g=para.phy.g0*ones(n_int,1);
  h=para.phy.h0*ones(n_int,1);
  para.phy.g=g;
  para.phy.h=h;
else
  g=para.phy.g;
  h=para.phy.h;
end
Cb=(1-g.*h.*h)./(g.*h.*h)-(g-1)./g;

% construct postion vectors
[ r_pos,th_tilt,dr,gamma_t,taper,xp,zp]=buildpos;


% construct other Matrices
X1=ka0*taper;
Tmp=h(:,ones(1,n))';
X2=X1./Tmp;
Dtheta=th_tilt(:,ones(1,m))'- th(:,ones(1,n_int));
Cos_dtheta=abs(cos(Dtheta));   % choose different local coordinates to
                               % avoid negtive argument of Bessel function
Gamma_t=gamma_t(:,ones(1,m))';
Theta=th(:,ones(1,n_int));
Dgamma=Gamma_t-Theta;
Cos_dgamma=cos(Dgamma);
term0=L_a*ka0*(r_pos./h)';
term1=h.*h.*Cb.*dr/4;
Jarr=1:m;					  % angle index for checking purpose
for J=1:length(Jarr)        			  % angle loop
% disp(sprintf(' j = %g, stop =%g',J,status.stop))
  if status.stop == 0
    j=Jarr(J);
    cos_dtheta=Cos_dtheta(j,:);
    Cos_th=cos_dtheta(ones(n,1),:);
    cos_dgamma=Cos_dgamma(j,:);
    Cos_gamma=cos_dgamma(ones(1,n),:);
    Arg=2*X2.*Cos_th+eps;
    J1x=besselj(1,Arg)./Arg;
    EXP=exp(1i*term0.*Cos_gamma);
    term2=(X2.*X2).*J1x.*EXP;
    f(:,j)=term2*term1+eps;
  else
    f=0;
    return
  end
end

