% spherical hankel function of the second kind
% function hn=sphhn2(n,x)

function hn=sphhn2(n,x)

hn=sphbeslj(n,x)-i*sphbesly(n,x);
