% function     [outx, outy]=nf_rgd_sft_fs(proc_flag,obj_type,scale,out_flag,para)
% returns the scattering pressure of a rigid/fixed or soft sphere at the nearfield/farfield 
% depending on the input parameter "obj_type"
% Assume a plane incident wave
%
% INPUTS:
%   proc_flag =	 1: scattering as a function of ka (dimensionless variable variable), 
%                   where k is wave number and a is the radius of the sphere
%                2: scattering as a function of the scattering angle (a variable)
%   obj_type  =	 1: rigid/fixed;    2: soft
%   scale	  =	 1: linear spacing; 2: log spacing
%   out_flag  =  1: modular of pressure
%                2: complex pressure
%   para ()       :   parameter array
%    para(1) = ns :  number of data points
%    para(2) = x0 :  starting value of the varible 
%    para(3) = xe :  ending value of the varible 
%    para(4) = theta0:  if proc_flag = 1  (degree)
%            = ka0:     if proc_flag = 2  (demensionless parameter)
%   para(5) = Nmax:  maximum number of modes (Nmax =1 for mode 0 only). If
%                    missing, using default Nmax = round(max(ka)) + 10
%   para(6) = r_to_a  : ratio of the range of the field point to the radius of the sphere
%
% OUTPUTS:
%       outx =  variable array generated according to the input parameters
%       outy =  computed scattering pressure, i.e.
%               the returned varable = outy(outx)
%               
%  By Dezhang Chu, NOAA Fisheries, NWFSC (dezhang.chu@noaa.gov), July 7, 2017  
%
function     [outx, outy]=nF_rgd_sft_fs(proc_flag,obj_type,scale,out_flag,para)

DEG2RAD=pi/180;
ns=para(1);
x0=para(2);
xe=para(3);
r_to_a=para(6);

if ( proc_flag == 1)   % scattering as a function of ka
    if (scale == 1)
        ka=linspace(x0,xe,ns);
    else
        ka=logspace(log10(x0),log10(xe),ns);
    end
    kr=ka*r_to_a;
    m=length(ka);
    theta=para(4)*DEG2RAD;
    if length(para) < 5
        Nmax=round(max(ka))+10;
    else
        Nmax=para(5);
    end
    x=cos(theta);
    n=0:(Nmax-1);
    pn=Pn(n,x);
    nl=-(2*n+1);
    if (obj_type == 1)
        djn=sphbesldj(n,ka,0);
        dyn=sphbesldy(n,ka,0);
        jnr=sphbeslj(n,kr);
        ynr=sphbesly(n,kr);
        hnr=jnr+i*ynr;
        for j=1:m
            s=(nl.*pn).*(djn(j,:).*hnr(j,:)./(djn(j,:)+i*dyn(j,:)));
            f(j)=sum(s);
        end
    else
        jn=sphbeslj(n,ka);
        yn=sphbesly(n,ka);
        for j=1:m
            s=(nl.*pn).*(jn(j,:).*hnr(j,:)./(jn(j,:)+i*yn(j,:)));
            f(j)=sum(s);
        end
    end
    outx=ka;
else                    %%% scattering as a function of scattering angle
    ka=para(4);
    kr=ka*r_to_a;
    theta=linspace(x0,xe,ns)*DEG2RAD;
    x=cos(theta);
    m=length(x);
    if length(para) < 5
        Nmax=round(max(ka))+10;
    else
        Nmax=para(5);
    end
    n=0:(Nmax-1);
    pn=Pn(n,x);
    nl=-(2*n+1);
    jnr=sphbeslj(n,kr);
    ynr=sphbesly(n,kr);
    hnr=jnr+i*ynr;
    if (obj_type == 1)
        djn=sphbesldj(n,ka,0);
        dyn=sphbesldy(n,ka,0);
        bn=djn./(djn+i*dyn);
        for j=1:m
            s=(nl.*pn(j,:)).*hnr.*bn;
            f(j)=sum(s);
        end
    else
        jn=sphbeslj(n,ka);
        yn=sphbesly(n,ka);
        bn=jn./(jn+i*yn);
        for j=1:m
            s=(nl.*pn(j,:)).*hnr.*bn;
            f(j)=sum(s);
        end
    end
    outx=theta;
end
if out_flag ==  1
    outy=abs(f)./ka;
elseif out_flag == 2 		% normalized complex scattering amplitude
    outy=f;
else
    errordlg('''out_flag'' must be within 1-4, try again !','Wrong Parameter' );
    outy=[];
end
