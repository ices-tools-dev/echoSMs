% spherical hankel function of the first kind
% function hn=sphhn1(n,x)

function hn=sphhn1(n,x)

hn=sphbeslj(n,x)+i*sphbesly(n,x);
