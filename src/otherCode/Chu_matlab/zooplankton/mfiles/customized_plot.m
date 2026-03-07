%% customized plot

figure(2)
freq=dat.var;
TS=dat.fun;
freq_i=[38 120 200];
TS_i=interp1(freq,TS,freq_i);


plot(freq,TS,'-',freq_i,TS_i,'s-r')
diff(TS_i)
