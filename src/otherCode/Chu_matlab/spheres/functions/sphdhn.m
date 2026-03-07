% derivative of the spherical hankel function
% function dhn=sphdhn(n,x,flag,hn)
%  flag = 0: without yn0
%       = 1: do not compute yn0, with yn0 as input
%  dhn(i)=i*hn(i)/x-hn(i+1)

function dhn=sphdhn(n,x,flag,hn)

if nargin <= 3
   dhn=sphbesldj(n,x)+i*sphbesldy(n,x);
elseif flag == 1
   dhn=sphbesldj(n,x,flag,real(hn))+i*sphbesldy(n,x,flag,imag(hn));
end   
   
