% scattering by an elastic sphere in near and far field
% function     [outx, outy]=elastic_fs(proc_flag,scale,out_flag,para)
% proc_flag =	 1: vs. ka;         2: vs. angle
% scale	    =	 1: linear spacing; 2: log spacing for proc_flag = 1
%                 for proc_flag = 2, scale is auumed linear
% out_flag  =    1: modular of form function
%		 2: complex form function
%		 3: modular of scattering amplitude normalized by (a*sqrt(pi))
%		 4: complex scattering amplitude normalized by (a*sqrt(pi))
% para ()   :   parameter array
%  para(1) = ns   :  number of data points
%  para(2) = x0   :  starting value for varible 1
%  para(3) = xe   :  ending value for varible 1
%  para(4) = g    :  rho2/rho1
%  para(5) = hc   :  c2L/c1       c2L: longitudinal sound speed of the sphere
%  para(6) = hs   :  c2T/c1       cT2: transverse sound speed of the sphere
%  para(7) = theta0  for proc_flag = 1  (degree)
%            theta0 = 180 for backscattering
%          = ka0     for proc_flag = 2 
%  para(8) = r_to_a  : ratio of the range of the field point to the radius of the sphere


function     [outx, outy]=nf_elastic_fs(proc_flag,scale,out_flag,para)
% outx =  ka   			  for  proc_flag = 1
%          incident angle (deg)    for  proc_flag = 2
% outy    			depends on out_flag

DEG2RAD=pi/180;
RAD2DEG=180/pi;
ns=para(1);
x0=para(2);
xe=para(3);
g=para(4);		
hc=para(5);
hs=para(6);
r_to_a=para(8);

if ( proc_flag == 1)
   if (scale == 1)
     ka1=linspace(x0,xe,ns);
   else
     ka1=logspace(x0,xe,ns);
   end
   kr=ka1*r_to_a;
   ka2L=ka1/hc;
   ka2s=ka1/hs;
   m=length(ka1);
   Nmax=max(ka1)+10;
   theta=para(7)*DEG2RAD;
   x=cos(theta);
   n=0:Nmax;
   pn=Pn(n,x);
   nl=(2*n+1);
   jn1=sphbeslj(n,ka1);
   yn1=sphbesly(n,ka1);
   djn1=sphbesldj(n,ka1,1,jn1);
   dyn1=sphbesldy(n,ka1,1,yn1);
   jn2L=sphbeslj(n,ka2L);
   djn2L=sphbesldj(n,ka2L,1,jn2L);
   jn2s=sphbeslj(n,ka2s);
   djn2s=sphbesldj(n,ka2s,1,jn2s);
   jnr=sphbeslj(n,kr);
   ynr=sphbesly(n,kr);
   hnr=jnr+i*ynr;
   for j=1:m
      nn=n.*n+n;
      tan1=-ka2L(j)*djn2L(j,:)./jn2L(j,:);
      tan2=-ka2s(j)*djn2s(j,:)./jn2s(j,:);
      tan3=-ka1(j)*djn1(j,:)./jn1(j,:);
      tan_beta=-ka1(j)*dyn1(j,:)./yn1(j,:);
      tan_del=-jn1(j,:)./yn1(j,:);
      d1=tan1+1;
      d2=nn-1-ka2s(j)^2/2+tan2;
      term1a=tan1./d1;
      term1b=nn./d2;
      term2a=(nn-ka2s(j)^2/2+2*tan1)./d1;
      term2b=nn.*(tan2+1)./d2;
      td=-0.5*ka2s(j)^2*(term1a-term1b)./(term2a-term2b);
      tan_phi=-td/g;
      tan_eta=tan_del.*(tan_phi+tan3)./(tan_phi+tan_beta);
      cos_eta=1./sqrt(1+tan_eta.*tan_eta);
      sin_eta=tan_eta.*cos_eta;
      bn=sin_eta.*(i*cos_eta-sin_eta);      % i*exp(i*eta)
      s=nl.*pn.*bn.*hnr(j,:).*(sqrt(-1)).^(n+1);
      f(j)=sum(s);
      outx=ka1;
   end
else
   ka1=para(7);
   ka2L=ka1/hc;
   ka2s=ka1/hs;
   kr=ka1*r_to_a;
   theta=linspace(x0,xe,ns)*DEG2RAD;
   x=cos(theta);
   m=length(x);
   Nmax=max(ka1)+10;
   n=0:Nmax;
   pn=Pn(n,x);
   nl=(2*n+1);
   jn1=sphbeslj(n,ka1);
   yn1=sphbesly(n,ka1);
   djn1=sphbesldj(n,ka1,1,jn1);
   dyn1=sphbesldy(n,ka1,1,yn1);
   jn2L=sphbeslj(n,ka2L);
   djn2L=sphbesldj(n,ka2L,1,jn2L);
   jn2s=sphbeslj(n,ka2s);
   djn2s=sphbesldj(n,ka2s,1,jn2s);
   jnr=sphbeslj(n,kr);
   ynr=sphbesly(n,kr);
   hnr=jnr+i*ynr;
   nn=n.*n+n;
      tan1=-ka2L*djn2L./jn2L;
      tan2=-ka2s*djn2s./jn2s;
      tan3=-ka1*djn1./jn1;
      tan_beta=-ka1*dyn1./yn1;
      tan_del=-jn1./yn1;
      d1=tan1+1;
      d2=nn-1-ka2s^2/2+tan2;
      term1a=tan1./d1;
      term1b=nn./d2;
      term2a=(nn-ka2s^2/2+2*tan1)./d1;
      term2b=nn.*(tan2+1)./d2;
      td=-0.5*ka2s^2*(term1a-term1b)./(term2a-term2b);
      tan_phi=-td/g;
      tan_eta=tan_del.*(tan_phi+tan3)./(tan_phi+tan_beta);
      cos_eta=1./sqrt(1+tan_eta.*tan_eta);
      sin_eta=tan_eta.*cos_eta;
      bn=sin_eta.*(i*cos_eta-sin_eta);          % i*exp(i*eta)
   for j=1:m
      s=nl.*pn(j,:).*bn;
      f(j)=sum(s);
   end
   F=(1-g*hc*hc)/(g*hc*hc)+(1-g)/g*x;
   outx=theta;
end
ka=ka1;
if ( out_flag == 1 )			% modular of form function
   outy=abs(2*f./ka);		
elseif ( out_flag == 2 )		% complex form function
   outy=-i*2*f./ka;
elseif ( out_flag == 3 )		% modular of scattering amplitude
   outy=abs(f)./ka;
elseif ( out_flag == 4 )		% complex scattering amplitude
   outy=-i*f./ka;
else
   disp(' out_flag must be within 1-4, try again !');
end
