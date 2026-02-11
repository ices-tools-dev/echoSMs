%% replot results from Aubrey Espana, APL, UW
%% 5/1/2017
% click on rigid_sphere.fig to open the figure first

figure(2)
close(2)
a = 0.25;
d=get(gca,'children');

d1 = get(d(1));
ka1 = d1.XData;
TS1 = d1.YData;

d2 = get(d(2));
ka2 = d2.XData;
TS2 = d2.YData - 28;

figure(2)
plot(ka1, TS1, '.-', ka2, TS2, 'o-r')
xlabel('ka')
ylabel('RTS')
legend('COMSOL','Exact','location','southeast')