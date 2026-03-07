function		h=popupmenu_action(indx)
% checkbox action


switch indx
  case 1					 	% popupmenu 'variable'
    h=findobj(gcf,'Tag','PopupMenuVar');
    opt=get(h,'Value');
    h1=findobj(gcf,'Tag','StaticTextFreq');
    h2=findobj(gcf,'Tag','EditTextFreq');
    if opt == 2		% angle of orientation is the variable
      set([h1 h2],'Enable','on');
    else
      set([h1 h2],'Enable','off');
    end      
end