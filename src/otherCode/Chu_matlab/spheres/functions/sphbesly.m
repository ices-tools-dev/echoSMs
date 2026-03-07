% spherical bessel function of the second kind
% forward recurrence formula
% function      yn=sphbesly(n,x)

function      yn=sphbesly(n,x)



x=x(:);
Nmax=max(n+1);
Nmin=min(n+1);  
for j=1:Nmax
    if j==1
    yn(:,j)=-cos(x)./x;
    else
      if j==2
          yn(:,j)=-(cos(x)./x+sin(x))./x;
      else
          yn(:,j)=(2*j-3)*yn(:,j-1)./x-yn(:,j-2);
      end
    end
end
yn=yn(:,Nmin:Nmax);
