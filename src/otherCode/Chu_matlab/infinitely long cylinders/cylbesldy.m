% derivative of the spherical bessel function of the second kind
%  dYn(i)=i*Yn(i)/x-Yn(i+1)

function 	dYn=cylbesldy(n,x,flag,Yn0)

% flag = 0    : compute Yn 
% flag = 1    : do not compute Yn 

if nargin < 3
  flag=0;
end

x=x(:);
if ( flag == 0 )
  Yn=cylbesly(min(n):max(n)+1,x);
else
  Yn_max=cylbesly(max(n)+1,x);
  Yn=[Yn0 Yn_max];
end

if (length(n) == 1)
  dYn=n*Yn(:,1)./x-Yn(:,2);
  return
else
  for i=1:max(n)-min(n)+1
    dYn(:,i)=n(i)*Yn(:,i)./x-Yn(:,i+1);
  end
end
