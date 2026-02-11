% construct inhomogeneous g and h based on given parameter
function    [g,h,Cb,FlucVal]=inhom_gh

global para
n_int=para.simu.ni;
g0=para.phy.g0;
h0=para.phy.h0;
SegNo=para.phy.seg_no;
lcorr=round(para.phy.corrL*n_int/100);
VarStd_g=para.phy.g_std;
VarStd_h=para.phy.h_std;
prop_fac=VarStd_h/VarStd_g;

if get(findobj(gcf,'Tag','CheckboxInhomo'),'Value') == 0
  g=g0*ones(n_int,1);
  h=h0*ones(n_int,1);
  FlucVal=zeros(n_int,1);
  Cb=(1-g.*h.*h)./(g.*h.*h)-(g-1)./g;
  return
end

figure(2)

if ( lcorr < 0.001 | SegNo <= 8) % construct un-correlated randomized g ang h profile
 disp(' < 7 segment ')
 OK=0;
 while OK ~= 1
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

    disp(sprintf('g: mean = %g',Valmean))
    disp(sprintf('g: std = %g',Valstd))

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

    disp(sprintf('h: mean = %g',Valmean))
    disp(sprintf('h: std = %g',Valstd))

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
  plot(1:n_int,g,1:n_int,h)
  s=input('OK (y/n)?  ','s');
  s='y';
  if ~isempty(s)
    if s == 'y'
      OK=1;
%      fname=input('Specify the FileName to save this profile =  ','s');
%      cmd=['save ' fname ' g h ft VarStd_g VarStd_h n_int SegNo'];
%      eval(cmd)
    end
  end
 end
 
else		% construct correlated randomized g ang h profile
	        % Gaussian correlation function
 z=linspace(0,n_int,n_int)-n_int/2;
 Rg = exp(-0.5*(z/lcorr).^2);  % sqrt(correlation function)
 P1=fft(Rg);
 Pphs=phase(P1);
 P=abs(P1);
 F=sqrt(P);
 OK=0;
 while OK ~= 1
  if rem(n_int,2) == 0 		% n_int is an even number
    n=n_int/2;
    phs=2*pi*rand(1,n-1);	
    F(2:n)=F(2:n).*exp(1i*phs); % negative frequency component
    phs_flip=-fliplr(phs);     % fliped phase
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
  disp(sprintf('std(ft) = %g, <ft> = %g',std(ft),mean(ft)))

% check 

  F1=fft(ft);
  Pc=F1.*conj(F1).*exp(1i*Pphs);
  Rx=xcorr(ft);
  subplot(311)
  plot(ft)
  ylabel('Fluctuation Func.')
  grid
  Rf=real(ifft(Pc));				% real function
  indx=1:n_int;
  subplot(312)
  hh=plot(indx,Rx(n_int-n:n_int+n-1),indx,Rf,'r');
  legend(hh,'Reconstructed Rx','Original Rx') 
  ylabel('AutoCorrelation Func.')
  grid

  subplot(313)
  g=g0*(1+ft);
  h=h0*(1+prop_fac*ft);
  hh=plot(indx,g,indx,h,'r');
  legend(hh,'h','g')
  xlabel('INDEX')
  ylabel('Constructed g and h')
  grid
  scl=axis;
  xt=0.2*scl(2);
  yt=scl(4)-scl(3);
  text(xt,0.9*yt+scl(3),sprintf('<g> = %6.5g',g0));
  text(0.4*scl(2),0.9*yt+scl(3),sprintf('<h> = %6.5g',h0));
  ft=ft(:);
  FlucVal=ft(:);
  g=g(:);
  h=h(:);

  %s=input('OK (y/n)?  ','s');
s='y';
  if ~isempty(s)
    if s == 'y'
      OK=1;
%      fname=input('Specify the FileName to save this profile =  ','s');
%      cmd=['save ' fname ' g h FlucVal VarStd_g VarStd_h lcorr n_int SegNo'];
 %     eval(cmd)
    end
  end
 end				% while OK loop
 Cb=(1-g.*h.*h)./(g.*h.*h)-(g-1)./g;
end

close(2)