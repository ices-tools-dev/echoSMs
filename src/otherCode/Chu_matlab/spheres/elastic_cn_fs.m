% function     [outx, outy]=elastic_cn_fs(para)
% returns the scattering coeifficent cn (Faran)
%
% INPUTS:
% para ()   :   parameter array
%  para(1) = ns   :  number of data points
%  para(2) = x0   :  starting value of the varible 
%  para(3) = xe   :  ending value of the varible 
%  para(4) = g    :  rho2/rho1, where rho1 is the density of the surrounding
%                    fluid and rho2 is the density of the elastic sphere
%  para(5) = hc   :  c2L/c1       c2L: longitudinal sound speed of the sphere
%  para(6) = hs   :  c2T/c1       cT2: transverse sound speed of the sphere
%  para(7) = Nmax:  maximum number of modes (Nmax =1 for mode 0 only). If
%                    missing, using default Nmax = round(max(ka1)) + 10
%
% OUTPUTS:
%       outx =  variable array generated according to the input parameters
%       outy =  computed scattering form function/amplitude, i.e.
%               the returned varable = outy(outx)
%               
%  By Dezhang Chu, Woods Hole Oceanographic Institution (dchu@whoi.edu), Oct. 3, 2006  

function     [outx, outy]=elastic_cn_fs(para)
% outx =  ka   			  for  proc_flag = 1
%          incident angle (deg)    for  proc_flag = 2
% outy    			depends on out_flag

% DEG2RAD=pi/180;
% RAD2DEG=180/pi;
ns=para(1);
x0=para(2);
xe=para(3);
g=para(4);
hc=para(5);
hs=para(6);

ka1=linspace(x0,xe,ns);
ka2L=ka1/hc;
ka2s=ka1/hs;
m=length(ka1);
if length(para) < 7
    Nmax=round(max(ka1))+10;
else
    Nmax=para(7);
end
%theta=para(7)*DEG2RAD;
%x=cos(theta);
n=0:(Nmax-1);
nl=(2*n+1);
jn1=sphbeslj(n,ka1);
yn1=sphbesly(n,ka1);
djn1=sphbesldj(n,ka1,1,jn1);
dyn1=sphbesldy(n,ka1,1,yn1);
jn2L=sphbeslj(n,ka2L);
djn2L=sphbesldj(n,ka2L,1,jn2L);
jn2s=sphbeslj(n,ka2s);
djn2s=sphbesldj(n,ka2s,1,jn2s);
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
    bn=sin_eta.*(1i*cos_eta-sin_eta);      % i*exp(i*eta)
    cn(j,n+1)=nl.*bn;
end
outx=ka1(:);
% outy=-i*2*cn./repmat(outx,1,Nmax);
outy=cn;

return
