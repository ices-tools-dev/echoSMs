% Legendre Polynomial Pn(cos(theta))= Pn (n,x);

function      ans=Pn(n,x)

x=x(:);
m=length(x);
if ( max(abs(x)) > 1) 
  disp( '|x| must be smaller than 1')
  return
end
pn(:,1)=ones(m,1);
pn(:,2)=x;
for i=1:max(n)-1
   pn(:,i+2)=((2*i+1)*x.*pn(:,i+1)-i*pn(:,i))/(i+1);
end
ans=pn(:,n+1);
