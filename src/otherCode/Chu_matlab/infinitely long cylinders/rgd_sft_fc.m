% function     [outx, outy]=rgd_sft_fc(proc_flag,obj_type,scale,out_flag,para)
% returns the scattering form function of an infinitely long cylinder or the normalized 
% scattering amplitude of a finite length cylinder (L), depending on the input parameter 
% due to a plane incident wave. The cylinder is either rigid/fixed or soft (pressure release)
%
% INPUTS:
%   proc_flag =	 1: scattering as a function of ka (dimensionless variable variable), 
%                   where k is wave number and a is the radius of the cylinder
%                2: scattering as a function of the scattering angle (a variable)
%   obj_type  =	 1: rigid/fixed;    2: soft
%   scale	  =	 1: linear spacing; 2: log spacing
%   out_flag  =  1: modular of form function
%                2: complex form function
%                3: modular of scattering amplitude normalized by the length of the cylinder 
%                4: complex scattering amplitude normalized by the length of the cylinder 
%   para ()       :   parameter array
%    para(1) = ns :  number of data points
%    para(2) = x0 :  starting value of the varible 
%    para(3) = xe :  ending value of the varible 
%    para(4) = theta0:  if proc_flag = 1  (degree)
%            = ka0:     if proc_flag = 2  (demensionless parameter)
%   para(5) = Nmax:  maximum number of modes (Nmax =1 for mode 0 only). If
%                    missing, using default Nmax = round(max(ka)) + 10
%
% OUTPUTS:
%       outx =  variable array generated according to the input parameters
%       outy =  computed scattering form function/amplitude, i.e.
%               the returned varable = outy(outx)
%               
%  By Dezhang Chu, Woods Hole Oceanographic Institution (dchu@whoi.edu), Oct. 14, 2006  
%
function     [outx, outy]=rgd_sft_fc(proc_flag,obj_type,scale,out_flag,para)

DEG2RAD=pi/180;
ns=para(1);
x0=para(2);
xe=para(3);

if ( proc_flag == 1)
   if (scale == 1)
     ka=linspace(x0,xe,ns);
   else
     ka=logspace(log10(x0),log10(xe),ns);
   end
   m=length(ka);
   theta=para(4)*DEG2RAD;
   if length(para) < 5
      Nmax=round(max(ka))+10;
   else
      Nmax=para(5);
   end
   n=0:(Nmax-1);
   pn=cos(theta*n);
   em=2*[0.5 ones(1,Nmax-1)];
   if (obj_type == 1)
      dJn=cylbesldj(n,ka,0);
      dYn=cylbesldy(n,ka,0);
      for j=1:m
        s=(em.*pn).*(dJn(j,:)./(dJn(j,:)+i*dYn(j,:)));
        f(j)=sum(s);
      end
   else
      Jn=cylbeslj(n,ka);
      Yn=cylbesly(n,ka);
      for j=1:m
         s=(em.*pn).*(Jn(j,:)./(Jn(j,:)+i*Yn(j,:)));
%disp(conj(s'));pause
         f(j)=sum(s);
      end
   end
   outx=ka;
else
   ka=para(4);
   theta=linspace(x0,xe,ns)*DEG2RAD;
   m=length(theta);
   if length(para) < 5
     Nmax=round(max(ka))+10;
   else
     Nmax=para(5);
   end
   n=0:(Nmax-1);
   pn=cos(theta'*n);
   em=2*[0.5 ones(1,Nmax-1)];
   if (obj_type == 1)
      dJn=cylbesldj(n,ka,0);
      dYn=cylbesldy(n,ka,0);
      bn=dJn./(dJn+i*dYn);
      for j=1:m
        s=(em.*pn(j,:)).*bn;
        f(j)=sum(s);
      end
   else
      Jn=cylbeslj(n,ka);
      Yn=cylbesly(n,ka);
      bn=Jn./(Jn+i*Yn);
      for j=1:m
        s=(em.*pn(j,:)).*bn;
        f(j)=sum(s);
      end
   end      
   F=-0.5+cos(theta);
   outx=theta;
end
if ( out_flag == 1 )			% modular of form function
   outy=abs(2*f./sqrt(pi*ka));		
elseif ( out_flag == 2 )		% complex form function
   outy=2*exp(i*pi/4)*f./sqrt(pi*ka);
   outy=2*f./sqrt(pi*ka);
elseif ( out_flag == 3 )		% modular of normalized scattering amplitude
   outy=abs(f)/pi;
elseif ( out_flag == 4 )		% normalized complex scattering amplitude
   outy=-i*f/pi;
else
   errordlg('''out_flag'' must be within 1-4, try again !','Wrong Parameter' );
   outy=[];
end
