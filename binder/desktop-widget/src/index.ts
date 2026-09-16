// Opens the VNC desktop (served by jupyter-remote-desktop-proxy at /desktop)
// as a docked JupyterLab tab.
//
// - Launcher tile and command palette entry "Open Desktop Panel"
// - Opens automatically only with ?autoOpenDesktop=1 in the lab URL
import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {
  ICommandPalette,
  MainAreaWidget,
  WidgetTracker
} from '@jupyterlab/apputils';
import { PageConfig } from '@jupyterlab/coreutils';
import { ILauncher } from '@jupyterlab/launcher';
import { LabIcon } from '@jupyterlab/ui-components';
import { Widget } from '@lumino/widgets';

const COMMAND_ID = 'desktop-widget:open';
const NAMESPACE = 'desktop-widget';

const desktopIcon = new LabIcon({
  name: 'desktop-widget:icon',
  svgstr:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16">' +
    '<path class="jp-icon3" fill="#616161" d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7v2H8v2h8v-2h-2v-2h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H3V4h18v12z"/>' +
    '</svg>'
});

const startupFlag = (name: string, defaultValue: boolean): boolean => {
  const raw = new URLSearchParams(window.location.search).get(name);
  if (raw === null) {
    return defaultValue;
  }
  return !['0', 'false', 'off', 'no'].includes(raw.trim().toLowerCase());
};

class DesktopContent extends Widget {
  constructor() {
    super();
    this.addClass('jp-DesktopWidget');
    this.node.style.height = '100%';

    const iframe = document.createElement('iframe');
    iframe.src = `${PageConfig.getBaseUrl()}desktop`;
    iframe.setAttribute('title', 'Desktop');
    iframe.setAttribute('allow', 'clipboard-read; clipboard-write');
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = '0';

    this.node.appendChild(iframe);
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'desktop-widget:plugin',
  autoStart: true,
  requires: [ILayoutRestorer],
  optional: [ILauncher, ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    restorer: ILayoutRestorer,
    launcher: ILauncher | null,
    palette: ICommandPalette | null
  ) => {
    const tracker = new WidgetTracker<MainAreaWidget<DesktopContent>>({
      namespace: NAMESPACE
    });
    let widget: MainAreaWidget<DesktopContent> | null = null;

    app.commands.addCommand(COMMAND_ID, {
      label: 'Open Desktop Panel',
      caption: 'Show the remote desktop next to the notebook',
      icon: desktopIcon,
      execute: async () => {
        if (widget === null || widget.isDisposed) {
          widget = new MainAreaWidget({ content: new DesktopContent() });
          widget.id = 'desktop-widget';
          widget.title.label = 'Desktop';
          widget.title.icon = desktopIcon;
          widget.title.closable = true;
          await tracker.add(widget);
        }
        if (!widget.isAttached) {
          app.shell.add(widget, 'main', { mode: 'split-right' });
        }
        app.shell.activateById(widget.id);
        return widget;
      }
    });

    void restorer.restore(tracker, {
      command: COMMAND_ID,
      name: () => 'desktop'
    });

    if (launcher) {
      launcher.add({ command: COMMAND_ID, category: 'Other', rank: 0 });
    }
    if (palette) {
      palette.addItem({ command: COMMAND_ID, category: 'Desktop' });
    }

    void app.restored.then(async () => {
      if (startupFlag('autoOpenDesktop', false)) {
        await app.commands.execute(COMMAND_ID);
      }
    });
  }
};

export default plugin;
