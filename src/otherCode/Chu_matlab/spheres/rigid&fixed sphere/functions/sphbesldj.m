% derivative of the spherical bessel function of the first kind
% function 	djn=sphbesl(n,x,flag,jn0)
%  flag = 0: compute jn0
%       = 1: do not compute jn0, with jn0 as input
%  djn(i)=i*jn(i)/x-jn(i+1)

function 	djn=sphbesldj(n,x,flag,jn0)


if nargin < 3
  flag=0;
end

indx=find(abs(x) < 1e-14);
x(indx)=1e-10*ones(size(indx));

x=x(:);
m=length(x);
if ( flag == 0 )
  jn=sphbeslj(min(n):max(n)+1,x);
else
  jn_max=sphbeslj(max(n)+1,x);
  jn=[jn0 jn_max];
end

if (length(n) == 1)
  djn=n*jn(:,1)./x-jn(:,2);
  return
else
  for i=1:max(n)-min(n)+1
    djn(:,i)=n(i)*jn(:,i)./x-jn(:,i+1);
  end
end

