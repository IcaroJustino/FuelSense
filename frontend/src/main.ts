import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import { registerChartJS } from './app/chartConfig';
import { registerLocaleData } from '@angular/common';
import localePt from '@angular/common/locales/pt';
registerLocaleData(localePt);
registerChartJS();

bootstrapApplication(App, appConfig).catch((err) => console.error(err));
