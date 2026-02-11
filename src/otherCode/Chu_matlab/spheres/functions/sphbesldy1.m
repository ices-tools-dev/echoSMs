% derivative of the spherical bessel function of the second kind
% dyn(i)=yn(i-1)-(i+1)*yn(i)/x

function 	dyn=sphbesl(n,x,flag,yn0)

% flag = 0    : compute yn 
% flag = 1    : do not compute yn 

x=x(:);
if ( flag == 0 )
  if ( min(n) ~= 0)
    yn=sphbesly(min(n)-1:max(n),x);
  else
    yn=sphbesly(min(n):max(n),x);
  end
else
  if ( min(n) ~= 0)
    yn_min=sphbesly( min(n)-1,x);
    yn=[yn_min yn0];
  else
    yn=yn0;
  end
end

if ( min(n) == 0)
   y1=-cos(x)./(x.*x)-sin(x)./x;
   dyn(:,1)=-y1;
   if ( length(n) == 1)
       return
   else
     for i=2:max(n)-min(n)+1
       dyn(:,i)=yn(:,i-1)-(n(i)+1)*yn(:,i)./x;
     end
   end
else
   for i=1:max(n)-min(n)+1
     dyn(:,i)=yn(:,i)-(n(i)+1)*yn(:,i+1)./x;
   end
end


