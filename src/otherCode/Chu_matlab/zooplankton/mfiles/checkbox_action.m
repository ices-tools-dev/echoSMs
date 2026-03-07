function		h=checkbox_action(indx)
% checkbox action

global para

switch indx
  case 1					% Length average
    h=findobj(gcf,'Tag','CheckboxLengthAve');
    h1=findobj(gcf,'Tag','StaticTextStdL');
    h2=findobj(gcf,'Tag','EditTextStdL');
    h3=findobj(gcf,'Tag','StaticTextDL');
    h4=findobj(gcf,'Tag','EditTextDL');
    ha=[h1 h2 h3 h4];
    if get(h,'Value') == 1
      set(ha,'Enable','on');
    else
      set(ha,'Enable','off');
    end
  case 2					% shape profile
    h=findobj(gcf,'Tag','CheckboxProfile');
    h1=findobj(gcf,'Tag','StaticTextTaperSmooth');
    h2=findobj(gcf,'Tag','EditTextTaperSmooth');
    h3=findobj(gcf,'Tag','StaticTextAxisSmooth');
    h4=findobj(gcf,'Tag','EditTextAxisSmooth');
	 h5=findobj(gcf,'Tag','PushbuttonBrowse');
    ha=[h1 h2 h3 h4 h5];
    h1=findobj(gcf,'Tag','StaticTextRho_L');
    h2=findobj(gcf,'Tag','EditTextRho_L');
    h3=findobj(gcf,'Tag','StaticTextL_a');
    h4=findobj(gcf,'Tag','EditTextL_a');
    h5=findobj(gcf,'Tag','StaticTextTaperOrder');
    h6=findobj(gcf,'Tag','EditTextTaperOrder');
    hb=[h1 h2  h5 h6];
    if get(h,'Value') == 1
      set(ha,'Enable','on');
      set(hb,'Enable','off');
    else
      set(ha,'Enable','off');
      set(hb,'Enable','on');
    end
  case 3					% orientation average
    h=findobj(gcf,'Tag','CheckboxOrientAve');
    h1=findobj(gcf,'Tag','RadiobuttonUniPDF');
    h2=findobj(gcf,'Tag','RadiobuttonGaussPDF');
    h3=findobj(gcf,'Tag','StaticTextStdTheta');
    h4=findobj(gcf,'Tag','EditTextStdTheta');
    h5=findobj(gcf,'Tag','StaticTextDtheta');
    h6=findobj(gcf,'Tag','EditTextDtheta');
    ha=[h1 h2 h3 h4 h5 h6];
    if get(h,'Value') == 1
      set(ha,'Enable','on');
    else
      set(ha,'Enable','off');
    end
  case 4					% inhomogenous body
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
    if get(h,'Value') == 1 
      set(ha,'Enable','on');
      hp=gh_figure;
    else
       set(ha,'Enable','off');
   end
end