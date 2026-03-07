% derivative of the cylindrical bessel function of the first kind
%  dJn(i)=i*Jn(i)/x-Jn(i+1)

function 	dJn=clybesldj(n,x,flag,Jn0)

% flag = 0    : compute Jn 
% flag = 1    : do not compute Jn 

if nargin < 3
  flag=0;
end

x=x(:);
m=length(x);
if ( flag == 0 )
  Jn=cylbeslj(min(n):max(n)+1,x);
else
  Jn_max=cylbeslj(max(n)+1,x);
  Jn=[Jn0 Jn_max];
end

if (length(n) == 1)
  dJn=n*Jn(:,1)./x-Jn(:,2);
  return
else
  for i=1:max(n)-min(n)+1
    dJn(:,i)=n(i)*Jn(:,i)./x-Jn(:,i+1);
  end
end

