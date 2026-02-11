% simulation average backscattering over orienation and length by euphausiid and copopod 
% 
function			p=bscat;
global para status misc dat

status.stop=0;
% limits of angle variation
if para.simu.var_indx == 2
    if para.orient.ave_flag == 1
        if para.orient.PDF == 1		% uniform PDF
            ang_max=para.simu.var1+para.orient.PDF_para;
            ang_min=para.simu.var0-para.orient.PDF_para;
        else								% Gaussian PDF
            ang_max=para.simu.var1+3*para.orient.PDF_para;
            ang_min=para.simu.var0-3*para.orient.PDF_para;
        end
        if ang_min < para.orient.ang0
            para.orient.ang0=ang_min;
            h=findobj(gcf,'Tag','EditTextTheta0');
            set(h,'String',num2str(para.orient.ang0));
        end
        if ang_max > para.orient.ang1
            para.orient.ang1=ang_max;
            h=findobj(gcf,'Tag','EditTextTheta1');
            set(h,'String',num2str(para.orient.ang1));
        end
        ang=ang_min:para.orient.dang:ang_max;
    else
        ang_min=para.simu.var0;
        ang_max=para.simu.var1;
        ang=linspace(ang_min,ang_max,para.simu.n);
    end
elseif para.orient.ave_flag == 1
    if para.orient.PDF == 1		% uniform PDF
        ang_min=para.orient.angm-para.orient.PDF_para;
        ang_max=para.orient.angm+para.orient.PDF_para;
    else								% Gaussian PDF
        ang_min=para.orient.angm-3.1*para.orient.PDF_para;
        ang_max=para.orient.angm+3.1*para.orient.PDF_para;
    end
    ang=ang_min:para.orient.dang:ang_max;
else
    ang_min=para.orient.angm;
    ang_max=para.orient.angm;
    ang=ang_min;
end

% limits of ka variation
a=para.shape.L/para.shape.L_a;							% mm															% a in mm and freq in kHz
switch  para.simu.var_indx
    case 1
        ka0=2*pi*para.simu.var0*a/misc.cw;		% a (mm) f(kHz)
        ka1=2*pi*para.simu.var1*a/misc.cw;
    case 2
        ka0=2*pi*para.simu.freq*a/misc.cw;
        ka1=ka0;
    case 3
        ka0=para.simu.var0;
        ka1=para.simu.var1;
end

if para.shape.ave_flag == 1
    ka_min=ka0*(1-3.1*para.shape.Lstd);
    ka_max=ka1*(1+3.1*para.shape.Lstd);
    nl=6*para.shape.Lstd/para.shape.dL;
else
    ka_min=ka0;
    ka_max=ka1;
    nl=1;
end
len_ave_para=[nl para.shape.Lstd];

Npts=para.simu.n;
if para.simu.var_indx == 2
    if para.shape.ave_flag == 1
        nl=6*para.shape.Lstd/para.shape.dL;
        kaL=linspace(ka0,ka1,1);
        ka=linspace(ka_min,ka_max,nl);
    else
        ka=ka0;
        kaL=ka;
    end
else
    if Npts == 1
        ka=ka_min;
        kaL=ka0;
    else
        ka=linspace(ka_min,ka_max,Npts);
        kaL=linspace(ka0,ka1,Npts);
    end
end

misc.ang=ang;
misc.ka=ka(:);

% conmpute scattering amplitude/L
[ka,ang,f]=DWBAbscat;
if status.stop == 1
    return
end
if para.simu.var_indx == 2
    angm=linspace(para.simu.var0,para.simu.var1,Npts);	% mean incident angle
    len_ave_para=[nl para.shape.Lstd];
    for i=1:Npts
        orient_ave_para=[angm(i) para.orient.PDF_para];
        if para.orient.ave_flag == 1
            f1=orient_ave(ang,f,para.orient.PDF,orient_ave_para);
        else
            f1=f(:,i);
        end
        f2(i)=length_ave(ka,kaL,f1,2,len_ave_para);
    end
else
    orient_ave_para=[para.orient.angm para.orient.PDF_para];
    f1=orient_ave(ang,f,para.orient.PDF,orient_ave_para);
    len_ave_para=[nl para.shape.Lstd];
    f2=length_ave(ka,kaL,f1,2,len_ave_para);
end

% convert output to the specified quantity
y=abs(f2);
ylab='NORMALIZED BACKSCATTERING AMPLITUDE (f_{bs}/L)';
switch para.simu.out_indx
    case 2
        y=y.*y;
        ylab='SCATTERING CROSS SECTION (\sigma_{bs})';
    case 3
        y=20*log10(y*para.shape.L)-60;	% L: mm -> m
        ylab='TARGET STRENGTH (dB)';
    case 4
        y=20*log10(y);
        ylab='REDUCED TARGET STRENGTH (dB)';
end
switch para.simu.var_indx
    case 1
        xlab='FREQUENCY (kHz)';
    case 2
        xlab='ANGLE OF ORIENTATION';
    case 3
        xlab='ka';
end
var=linspace(para.simu.var0,para.simu.var1,para.simu.n);
p=plot(var,y,'linewidth',1.5);
xlabel(xlab);
ylabel(ylab);
dat.var=var;
dat.fun=y;
p=0;