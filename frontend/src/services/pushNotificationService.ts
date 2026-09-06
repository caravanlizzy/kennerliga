import { api } from 'boot/axios';

export type TPushDevicePayload = {
  token: string;
  platform: 'android' | 'ios' | 'web' | 'unknown';
  device_id?: string | null;
  app_version?: string | null;
  notify_registration_open?: boolean;
  notify_league_started?: boolean;
  notify_active_player?: boolean;
};

export async function registerPushDevice(payload: TPushDevicePayload): Promise<void> {
  await api.post('/user/me/push-devices/', payload);
}

export async function deactivatePushDevice(token?: string): Promise<void> {
  await api.delete('/user/me/push-devices/', {
    data: token ? { token } : {},
  });
}
