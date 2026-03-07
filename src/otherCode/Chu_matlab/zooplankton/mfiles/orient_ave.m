% averaging over orientation


function      [outy]=orient_ave(ang,f,pdf_type,para)

% ang =       incident angle
% f   =       complex form function   # freq.  x  # orient. angle
% pdf_type =  distribution type       1: uniform  2: Gaussian
% para =      PDF parameters:
%         para(1) = <angle>
%         para(2) = range          for uniform
%		  = std(angle)     for Gaussian
%             

[n,m]=size(f);    % n = points in freq.,   m = points in orientation

%disp([n m])
if m == 1
  outy=f;
  return
end
if pdf_type == 1
   PDF=ones(m,1)/m;
else
   dang=ang(2)-ang(1);
   angm=para(1);
   angstd=para(2);
   PDF=dang*exp(-0.5*(ang(:)-angm).^2./angstd.^2)/(sqrt(2*pi)*angstd);
end

outy=sqrt((f.*conj(f))*PDF);

