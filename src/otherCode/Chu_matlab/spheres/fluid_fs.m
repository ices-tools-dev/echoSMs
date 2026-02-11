% function     [outx, outy]=fluid_fs(proc_flag,scale,out_flag,para)
% returns the scattering form function or normalized scattering amplitude, 
% depending on the input parameter, of a fluid sphere due to a plane incident wave
%
% INPUTS:
%   proc_flag =	 1: scattering as a function of ka (dimensionless variable variable), 
%                   where k is wave number and a is the radius of the sphere
%                2: scattering as a function of the scattering angle (a variable)
%   scale	  =	 1: linear spacing; 2: log spacing
%   out_flag  =  1: modular of form function
%                2: complex form function
%                3: modular of scattering amplitude normalized by the radius of the sphere 
%                4: complex scattering amplitude normalized by the radius of the sphere 
%   para ()       :   parameter array
%    para(1) = ns :  number of data points
%    para(2) = x0 :  starting value of the varible 
%    para(3) = xe :  ending value of the varible 
%    para(4) = g  :  rho2/rho1
%    para(5) = h  :  c2/c1
%    para(6) = theta0:  if proc_flag = 1  (degree)
%            = ka0:     if proc_flag = 2  (demensionless parameter)
%    para(7) = Nmax:  maximum number of modes (Nmax =1 for mode 0 only). If
%                    missing, using default Nmax = round(max(ka1)) + 10
%
% OUTPUTS:
%       outx =  variable array generated according to the input parameters
%       outy =  computed scattering form function/amplitude, i.e.
%               the returned varable = outy(outx)
%               
%  By Dezhang Chu, Woods Hole Oceanographic Institution (dchu@whoi.edu),
%  Oct. 3, 2006  

function     [outx, outy]=fluid_fs(proc_flag,scale,out_flag,para)

DEG2RAD=pi/180;
ns=para(1);
x0=para(2);
xe=para(3);
g=para(4);		
h=para(5);		
if ( proc_flag == 1)    %% scattering as a function of ka 
   if (scale == 1)    % Linear
     ka1=linspace(x0,xe,ns);
   else                % Log
     ka1=logspace(log10(x0),log10(xe),ns);
   end
   if length(para) < 7
     Nmax=round(max(ka1))+10;
   else
     Nmax=para(7);
   end
   ka2=ka1/h;
   m=length(ka1);
   theta=para(6)*DEG2RAD;
   x=cos(theta);
   n=0:(Nmax-1);
   pn1=Pn(n,x);
   nl=(2*n+1);
   jn1=sphbeslj(n,ka1);
   yn1=sphbesly(n,ka1);
   djn1=sphbesldj(n,ka1,1,jn1);
   dyn1=sphbesldy(n,ka1,1,yn1);
   jn2=sphbeslj(n,ka2);
   yn2=sphbesly(n,ka2);
   djn2=sphbesldj(n,ka2,1,jn2);
   term1=djn2.*yn1./(jn2.*djn1)-g*h*dyn1./djn1;
   term2=djn2.*jn1./(jn2.*djn1)-g*h;
   cn=term1./term2;
   bn=-1./(1+i*cn);
   for j=1:m
      s=nl.*pn1.*bn(j,:);
      f(j)=sum(s);
      S(j,1:Nmax)=s/ka1(j);
   end
%    save tmp  ka1 S
   outx=ka1;
else       %%% scattering as a function of scattering angle
   ka1=para(6);
   ka2=ka1/h;
   theta=linspace(x0,xe,ns)*DEG2RAD;
   x=cos(theta);
   m=length(x);
   if length(para) < 7
     Nmax=round(max(ka1))+10;
   else
     Nmax=para(7);
   end
   n=0:(Nmax-1);
   pn1=Pn(n,x);
   nl=(2*n+1);
   jn1=sphbeslj(n,ka1);
   yn1=sphbesly(n,ka1);
   djn1=sphbesldj(n,ka1,1,jn1);
   dyn1=sphbesldy(n,ka1,1,yn1);
   jn2=sphbeslj(n,ka2);
   yn2=sphbesly(n,ka2);
   djn2=sphbesldj(n,ka2,1,jn2);
   term1=djn2.*yn1./(jn2.*djn1)-g*h*dyn1./djn1;
   term2=djn2.*jn1./(jn2.*djn1)-g*h;
   cn=term1./term2;
   bn=-1./(1+i*cn);
   for j=1:m
      s=(nl.*pn1(j,:)).*bn;
      f(j)=sum(s);
   end
   F=(1-g*h*h)/(g*h*h)+(1-g)/g*x;
   outx=theta;
end
ka=ka1;
if ( out_flag == 1 )			% modular of form function
   outy=abs(2*f./ka);
elseif ( out_flag == 2 )		% complex form function
   outy=-i*2*f./ka;
elseif ( out_flag == 3 )		% modular of scattering amplitude
   outy=abs(f)./(sqrt(pi)*ka);
elseif ( out_flag == 4 )		% complex scattering amplitude
   outy=-i*f./(sqrt(pi)*ka);
else
   errordlg('''out_flag'' must be within 1-4, try again !','Wrong Parameter' );
   outy=[];
end
