% cylindrical bessel function Yn

function 	Yn=cylbesly(n,x)

indx=find(abs(x) < 1e-14);
x(indx)=1e-10*ones(size(indx));
if length(n) >= 1 & size(n,2) >= 1
  x=x(:);
end
[nu,z]=meshgrid(n,x);
Yn=bessely(nu,z);
if (length(n) == 1)
  Yn=Yn(:);
end
