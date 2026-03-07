% cylindrical bessel function Jn

function 	Jn=cylbeslj(n,x)

indx=find(abs(x) < 1e-14);
x(indx)=1e-10*ones(size(indx));
if length(n) >= 1 & size(n,2) >= 1
  x=x(:);
end
[nu,z]=meshgrid(n,x);
Jn=besselj(nu,z);
if ( length(nu) == 1)
  Jn=Jn(:);
end
