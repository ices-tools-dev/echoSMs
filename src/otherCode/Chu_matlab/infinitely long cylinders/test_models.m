% The elastic cylinder model
para = [500, 0.0, 2.0, 1.05, 1.02, 1.10, 180.0];
[x, y] = elastic_fc(1, 1, 1, para);
subplot(2,2,1)
plot(x, y)
title('Elastic cylinder')
xlabel('ka')
ylabel('Form function')

% The fluid cylinder model
para = [500, 0.0, 2.0, 1.05, 1.02, 180.0];
[x, y] = fluid_fc(1, 1, 1, para);
subplot(2,2,2)
plot(x, y)
title('Fluid cylinder')
xlabel('ka')
ylabel('Form function')

% The rigid fixed cylinder model
para = [500, 0.0, 2.0, 180.0];
[x, y] = rgd_sft_fc(1, 1, 1, 1, para);
subplot(2,2,3)
plot(x, y)
title('Rigid fixed cylinder')
xlabel('ka')
ylabel('Form function')

% The shell cylinder model
para = [500, 0.0, 2.0, 1.05, 1.07, 1.10, 1.09, 1.02, 1.01, 180.0];
[x, y] = shell_fc(1, 1, 1, para);
subplot(2,2,4)
plot(x, y)
title('Elastic cylinder shell')
xlabel('ka')
ylabel('Form function')
