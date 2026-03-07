% set loaded parameters to the panel display
function		h=set_parameters

global para

% set shape parameters
h=findobj(gcf,'Tag','EditTextLength');
set(h,'String',num2str(para.shape.L));

h=findobj(gcf,'Tag','CheckboxProfile');
if strcmp('-1',para.shape.prof_name(1:2)) == 1
   load_profile_flag=0;
else
   load_profile_flag=1;
end
h1=findobj(gcf,'Tag','StaticTextTaperSmooth');
h2=findobj(gcf,'Tag','EditTextTaperSmooth');
h3=findobj(gcf,'Tag','StaticTextAxisSmooth');
h4=findobj(gcf,'Tag','EditTextAxisSmooth');
h5=findobj(gcf,'Tag','PushbuttonBrowse');
ha=[h1 h2 h3 h4 h5];
h6=findobj(gcf,'Tag','StaticTextRho_L');
h7=findobj(gcf,'Tag','EditTextRho_L');
h8=findobj(gcf,'Tag','StaticTextL_a');
h9=findobj(gcf,'Tag','EditTextL_a');
h10=findobj(gcf,'Tag','StaticTextTaperOrder');
h11=findobj(gcf,'Tag','EditTextTaperOrder');
hb=[h6 h7 h8 h9 h10 h11];
set(h2,'String',num2str(para.shape.taper_sm));
set(h4,'String',num2str(para.shape.axis_sm));
disp('**** set_parameters! ****')
set(h7,'String',num2str(para.shape.rho_L));
set(h9,'String',num2str(para.shape.L_a));
set(h11,'String',num2str(para.shape.order));

if load_profile_flag == 1
  set(h,'Value',1);
  set(ha,'Enable','on');
  set(hb,'Enable','off');
else
  set(h,'Value',0);
  set(hb,'Enable','on');
  set(ha,'Enable','off');
end

h=findobj(gcf,'Tag','CheckboxLengthAve');
h1=findobj(gcf,'Tag','StaticTextStdL');
h2=findobj(gcf,'Tag','EditTextStdL');
h3=findobj(gcf,'Tag','StaticTextDL');
h4=findobj(gcf,'Tag','EditTextDL');
ha=[h1 h2 h3 h4];
set(h2,'String',num2str(para.shape.Lstd));
set(h4,'String',num2str(para.shape.dL));

if para.shape.ave_flag == 1
  set(h,'Value',1);
  set(ha,'Enable','on');
else
  set(h,'Value',0);
  set(ha,'Enable','off');
end

% set orientation parameters
h=findobj(gcf,'Tag','EditTextMeanTheta');
set(h,'String',num2str(para.orient.angm));
h=findobj(gcf,'Tag','EditTextTheta0');
set(h,'String',num2str(para.orient.ang0));
h=findobj(gcf,'Tag','EditTextTheta1');
set(h,'String',num2str(para.orient.ang1));

h=findobj(gcf,'Tag','CheckboxOrientAve');
h1=findobj(gcf,'Tag','RadiobuttonUniPDF');
h2=findobj(gcf,'Tag','RadiobuttonGaussPDF');
h3=findobj(gcf,'Tag','StaticTextStdTheta');
h4=findobj(gcf,'Tag','EditTextStdTheta');
h5=findobj(gcf,'Tag','StaticTextDtheta');
h6=findobj(gcf,'Tag','EditTextDtheta');
ha=[h1 h2 h3 h4 h5 h6];
set(h4,'String',num2str(para.orient.PDF_para));
set(h6,'String',num2str(para.orient.dang));
if para.orient.ave_flag == 1
   set(h,'Value',1);
   set(ha,'Enable','on');
   if para.orient.PDF == 1				% Uniform PDF
      set(h1,'Value',1);
      set(h2,'Value',0);
      set(h3,'String','Half range of theta');
   elseif  para.orient.PDF == 2		% Gaussian PDF  
      set(h1,'Value',0);
      set(h2,'Value',1);
      set(h3,'String','Std of theta');
   end
else
   set(h,'Value',0);
   set(ha,'Enable','off');
   set(h1,'Value',0);
   set(h2,'Value',1);
   set(h3,'String','Std of theta');
end


% set physical properties
h=findobj(gcf,'Tag','EditTextg');
set(h,'String',num2str(para.phy.g0));
h=findobj(gcf,'Tag','EditTexth');
set(h,'String',num2str(para.phy.h0));

h=findobj(gcf,'Tag','CheckboxInhomo');
h1=findobj(gcf,'Tag','StaticTextSegment');
h2=findobj(gcf,'Tag','EditTextSegment');
h3=findobj(gcf,'Tag','StaticTextStdg');
h4=findobj(gcf,'Tag','EditTextStdg');
h5=findobj(gcf,'Tag','StaticTextStdh');
h6=findobj(gcf,'Tag','EditTextStdh');
h7=findobj(gcf,'Tag','StaticTextCorrL');
h8=findobj(gcf,'Tag','EditTextCorrL');
ha=[h1 h2 h3 h4 h5 h6 h7 h8];
if ~isfield(para.phy, 'profile')
    para.phy.profile = 0;
end
if para.phy.profile == 1
   set(h,'Value',0);
   set(ha,'Enable','off');
else
   set(h,'Value',1);
   set(ha,'Enable','on');
end   
set(h2,'String',num2str(para.phy.seg_no));
set(h4,'String',num2str(para.phy.g_std));
set(h6,'String',num2str(para.phy.h_std));
set(h8,'String',num2str(para.phy.corrL));

% set simulation parameters
h1=findobj(gcf,'Tag','PopupMenuOutput');
h2=findobj(gcf,'Tag','PopupMenuVar');
h3=findobj(gcf,'Tag','EditTextNpts');
h4=findobj(gcf,'Tag','EditTextNint');
h5=findobj(gcf,'Tag','EditTextVar0');
h6=findobj(gcf,'Tag','EditTextVar1');
h7=findobj(gcf,'Tag','EditTextFreq');

set(h1,'Value',para.simu.out_indx);
set(h2,'Value',para.simu.var_indx);
set(h3,'String',num2str(para.simu.n));
set(h4,'String',num2str(para.simu.ni));
set(h5,'String',num2str(para.simu.var0));
set(h6,'String',num2str(para.simu.var1));
set(h7,'String',num2str(para.simu.freq));
h8=findobj(gcf,'Tag','StaticTextFreq');
if para.simu.var_indx == 2
  set([h7 h8],'Enable','on');
else
  set([h7 h8],'Enable','off');
end


