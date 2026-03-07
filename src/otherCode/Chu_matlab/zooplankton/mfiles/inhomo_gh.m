% construct inhomogeneous g and h based on given parameter
function    [g,h,Cb,FlucVal]=inhomo_gh

global para temp status

h0_2=findobj('Tag','Fig2');
hd_segno=findobj(h0_2,'Tag','EditText2SegNo1');
hd_mean_g=findobj(h0_2,'Tag','EditText2Meang1');
hd_mean_h=findobj(h0_2,'Tag','EditText2Meanh1');
hd_std_g=findobj(h0_2,'Tag','EditText2Stdg1');
hd_std_h=findobj(h0_2,'Tag','EditText2Stdh1');
hd_corrL=findobj(h0_2,'Tag','EditText2CorrL1');
para.phy.seg_no=str2num(get(hd_segno,'string'));
para.phy.g0=str2num(get(hd_mean_g,'string'));
para.phy.h0=str2num(get(hd_mean_h,'string'));
para.phy.g_std=str2num(get(hd_std_g,'string'));
para.phy.h_std=str2num(get(hd_std_h,'string'));
para.phy.corrL=str2num(get(hd_corrL,'string'));

n_int=para.simu.ni;
g0=para.phy.g0;
h0=para.phy.h0;
SegNo=para.phy.seg_no;
lcorr=round(para.phy.corrL*n_int/100);
VarStd_g=para.phy.g_std;
VarStd_h=para.phy.h_std;
prop_fac=VarStd_h/VarStd_g;

hd_segno=findobj(h0_2,'Tag','EditText2SegNo2');
hd_mean_g=findobj(h0_2,'Tag','EditText2Meang2');
hd_mean_h=findobj(h0_2,'Tag','EditText2Meanh2');
hd_std_g=findobj(h0_2,'Tag','EditText2Stdg2');
hd_std_h=findobj(h0_2,'Tag','EditText2Stdh2');
hd_corrL=findobj(h0_2,'Tag','EditText2CorrL2');
set(hd_segno,'string',num2str(SegNo));
set(hd_corrL,'string',num2str(para.phy.corrL));

if ( lcorr < 0.001 | SegNo <= 8) % construct un-correlated randomized g ang h profile
  if VarStd_g  > 1.e-8
    NoPerSeg=ceil(n_int/SegNo);     % Integration points in each segment
    FlucVal=VarStd_g*randn(1,SegNo);
    Valstd=std(FlucVal);
    Valmean=mean(FlucVal);
% adjust random variable to meet <>=0 sdt()= VarStd
    FlucVal=FlucVal-Valmean;
    FlucVal=VarStd_g*FlucVal/Valstd;
    Valstd=std(FlucVal);
    Valmean=mean(FlucVal);
    for j=1:n_int
      k=min(floor(j/NoPerSeg)+1,length(FlucVal));
      inhom_g(j)=FlucVal(k);
    end
  else
    inhom_g=zeros(n_int,1);
  end
  g=g0+inhom_g;

 if prop_fac == 0			% g & h no correlation
  if VarStd_h  > 1.e-8
    NoPerSeg=ceil(n_int/SegNo);     % Integration points in each segment
    FlucVal=VarStd_h*randn(1,SegNo);
    Valstd=std(FlucVal);
    Valmean=mean(FlucVal);
% adjust random variable to meet <>=0 sdt()= VarStd
    FlucVal=FlucVal-Valmean;
    FlucVal=VarStd_h*FlucVal/Valstd;
    Valstd=std(FlucVal);
    Valmean=mean(FlucVal);

    for j=1:n_int
      k=min(floor(j/NoPerSeg)+1,length(FlucVal));
      inhom_h(j)=FlucVal(k);
    end
  else
    inhom_h=zeros(n_int,1);
  end
  h=h0+inhom_h;
 else               % g and h are correlated
  h=h0+prop_fac*inhom_g;
 end

  g=g(:);
  h=h(:);
  Cb=(1-g.*h.*h)./(g.*h.*h)-(g-1)./g;
  ft=FlucVal;
  subplot(221)
  hh=plot(1:n_int,g,1:n_int,h,'r');
  xlabel('INDEX -1')
  ylabel('Constructed g and h');
  legend(hh,'h','g')
  subplot(222)
  hh=plot(0.5,0.5,'.');
  delete(hh)
else		% construct correlated randomized g ang h profile
	        % Gaussian correlation function
 z=linspace(0,n_int,n_int)-n_int/2;
 Rg = exp(-0.5*(z/lcorr).^2);  % sqrt(correlation function)
 P1=fft(Rg);
 Pphs=phase(P1);
 P=abs(P1);
 F=sqrt(P);
  if rem(n_int,2) == 0 		% n_int is an even number
    n=n_int/2;
    phs=2*pi*rand(1,n-1);	
    F(2:n)=F(2:n).*exp(1i*phs); % negative frequency component
    phs_flip=-fliplr(phs);     % flipping the phase
    F(n+2:n_int)=F(n+2:n_int).*exp(1i*phs_flip); % complex conjugate (pos. freq)	
  else                           % n_int is an odd number
    n=(n_int-1)/2;
    phs=2*pi*rand(1,n);	
    F(2:n+1)=F(2:n+1).*exp(1i*phs);			       % 
    phs_flip=-fliplr(phs);
    F(n+2:n_int)=F(n+2:n_int).*exp(1i*phs_flip);   % complex conjugate	
  end
  ftc=ifft(F);
  ft=real(ftc);ft=ft-mean(ft);
  fac=VarStd_h/std(ft);ft=fac*ft;

% check 

  indx=1:n_int;
  subplot(221)
  g=g0*(1+ft);
  h=h0*(1+prop_fac*ft);
  hh=plot(indx,g,indx,h,'r');
  xlabel('INDEX')
  ylabel('Constructed g and h')
  legend(hh,'h','g')
  grid

  F1=fft(ft);
  Pc=F1.*conj(F1).*exp(1i*Pphs);
  Rx=xcorr(ft);
  Rf=real(ifft(Pc));				% real function
  subplot(222)
  hh=plot(indx,Rx(n_int-n:n_int+n-1)/max(Rx(n_int-n:n_int+n-1))+1,indx,Rf/max(Rf)+1,'r');
  legend(hh,'Constructed Rx','Expected Rx') 
  xlabel('INDEX LAG')
  ylabel('AutoCorrelation Func.')
  grid

  scl=axis;
  xt=0.2*scl(2);
  yt=scl(4)-scl(3);
  ft=ft(:);
  FlucVal=ft(:);
  g=g(:);
  h=h(:);
  Cb=(1-g.*h.*h)./(g.*h.*h)-(g-1)./g;
end
set(hd_mean_g,'string',sprintf('%7.5g',mean(g)));
set(hd_std_g,'string',sprintf('%7.5g',std(g)));
set(hd_mean_h,'string',sprintf('%7.5g',mean(h)));
set(hd_std_h,'string',sprintf('%7.5g',std(h)));

temp.g=g;
temp.h=h;
temp.seg_no=SegNo;
temp.corrL=para.phy.corrL;
temp.Cb=Cb;
status.save=0;
% para.phy.g=g;
% para.phy.h=h;
% para.phy.seg_no=SegNo;

% h=findobj(gcf,'Tag','EditTextSegment');
% set(h,'String',para.phy.seg_no);
% h=findobj(gcf,'Tag','EditTextStdg');
% set(h,'String',std(para.phy.g));
% h=findobj(gcf,'Tag','EditTextStdh');
% set(h,'String',std(para.phy.h));
% close

