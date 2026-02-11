% construct a roughened elongated object based on a smoothed object
%clear

sd=0.03;
p=load('euphaus0.dat');
n=length(p(:,1));

d=randn(n,1);
D=p(:,5)-p(:,1);

ruf=D.*sd.*d;
taper=p(:,3).*(1+sd*d);

figure(1)
plot(p(:,2),p(:,4)-ruf,p(:,2),p(:,5)+ruf,p(:,2),p(:,1))
axis equal

figure(2)
plot(p(:,2),taper)

p(:,3)=taper;

save euphaus0_3p_ruf.dat p  -ascii