% function      [outy]=length_ave(ka0,ka1,f,pdf_type,para)
% averaging over leng
% ka0 =       original ka  ka=[ <a>-3*std_a  <a>+3*std_a]
% ka1 =       output ka 
% f   =       complex form function   # freq.(or ka)  x  # orient. angle
% pdf_type =  distribution type       1: uniform  2: Gaussian
% para =      PDF parameters:
%         para(1) = no. of bins for L PDF
%         para(2) = 1/3 max. diviation          for uniform
%		  				= std(length)    	        		for Gaussian
function      [outy]=length_ave(ka0,ka1,f,pdf_type,para)


n=length(ka1);    % n = points in freq. (ka)
m=round(para(1));
if m == 1
  outy=f;
  return
end
r_min=1-3*para(2);		% ratio = Lmin/<L>
r_max=1+3*para(2);		% ratio = Lmax/<L>
L=linspace(r_min,r_max,m);
dL=L(2)-L(1);
if pdf_type == 1
   PDF=ones(m,1)/m;
else
   Lm=1;			% 
   Lstd=para(2);		%      std(L)/<L>
   PDF=dL*exp(-0.5*(L(:)-Lm).^2./Lstd.^2)/(sqrt(2*pi)*Lstd);
end

sigma_bs0=f.*f;		% f sqrt of orientatipon averaged scat. cross-section
			% which is a real function
sigma_bs=zeros(m,n);		
for j=1:m
  ka2=L(j)*ka1;
  if max(ka2) > max(ka0) | min(ka2) < min(ka0)
    disp('ka is beyond ka0')
    disp([min(ka0) min(ka2)  max(ka2)  max(ka0) ])
    pause
  else
    sigma_bs(j,1:n)=L(j)*L(j)*PDF(j)*interp1(ka0,sigma_bs0,ka2);
  end
end

outy=sqrt(sum(sigma_bs));

