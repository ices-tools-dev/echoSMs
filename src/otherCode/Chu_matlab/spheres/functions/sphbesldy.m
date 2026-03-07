% derivative of the spherical bessel function of the second kind
% function 	dyn=sphbesldy(n,x,flag,jn0)
%  flag = 0: without yn0
%       = 1: do not compute yn0, with yn0 as input
%  dyn(i)=i*yn(i)/x-yn(i+1)

function 	dyn=sphbesldy(n,x,flag,yn0)

% flag = 0    : compute yn 
% flag = 1    : do not compute yn 

if nargin < 3
  flag=0;
end

x=x(:);
if ( flag == 0 )
  yn=sphbesly(min(n):max(n)+1,x);
else
  yn_max=sphbesly(max(n)+1,x);
  yn=[yn0 yn_max];
end

if (length(n) == 1)
  dyn=n*yn(:,1)./x-yn(:,2);
  return
else
  for i=1:max(n)-min(n)+1
    dyn(:,i)=n(i)*yn(:,i)./x-yn(:,i+1);
  end
end
