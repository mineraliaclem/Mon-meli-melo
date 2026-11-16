import sys,shutil,os
base='node_modules/@capacitor/local-notifications/android/src/main'
pk=base+'/java/com/capacitorjs/plugins/localnotifications/'
def patch(path,a,b,count=1):
    s=open(path,encoding='utf-8').read()
    if s.count(a)!=count:
        print('MOTIF INTROUVABLE dans',path,':',a[:70],s.count(a)); sys.exit(1)
    open(path,'w',encoding='utf-8').write(s.replace(a,b))
shutil.copy('android-native/QuickActionReceiver.java',pk+'QuickActionReceiver.java')
# 1. receiver dans le manifest du plugin
patch(base+'/AndroidManifest.xml','<receiver android:name="com.capacitorjs.plugins.localnotifications.NotificationDismissReceiver" />','<receiver android:name="com.capacitorjs.plugins.localnotifications.NotificationDismissReceiver" />\n        <receiver android:name="com.capacitorjs.plugins.localnotifications.QuickActionReceiver" android:exported="false" />')
# 2. boutons rapides -> broadcast au lieu d'ouvrir l'appli
M=pk+'LocalNotificationManager.java'
patch(M,'PendingIntent actionPendingIntent = PendingIntent.getActivity(','PendingIntent actionPendingIntent = isQuickAction(notificationAction.getId()) ? quickAction(localNotification, notificationAction.getId(), flags) : PendingIntent.getActivity(')
patch(M,'    @NonNull\n    private Intent buildIntent(','''    private boolean isQuickAction(String id) {
        return "taken".equals(id) || "skip".equals(id) || "tdone".equals(id) || "tlater".equals(id);
    }

    private PendingIntent quickAction(LocalNotification n, String actionId, int flags) {
        Intent in = new Intent(context, QuickActionReceiver.class);
        in.setAction("melimelo.quick." + actionId + "." + n.getId());
        in.putExtra(NOTIFICATION_INTENT_KEY, n.getId());
        in.putExtra(ACTION_INTENT_KEY, actionId);
        in.putExtra(NOTIFICATION_OBJ_INTENT_KEY, n.getSource());
        return PendingIntent.getBroadcast(context, n.getId() + actionId.hashCode(), in, flags);
    }

    @NonNull
    private Intent buildIntent(''')
# 3. méthode JS pour récupérer les évènements
P=pk+'LocalNotificationsPlugin.java'
s=open(P,encoding='utf-8').read()
i=s.rstrip().rfind('}')
add='''
    @PluginMethod
    public void getQuickEvents(PluginCall call) {
        JSObject ret = new JSObject();
        try {
            android.content.SharedPreferences sp = getContext().getSharedPreferences(QuickActionReceiver.PREFS, android.content.Context.MODE_PRIVATE);
            String s = sp.getString("events", "[]");
            sp.edit().remove("events").apply();
            ret.put("events", new JSONArray(s));
        } catch (Exception e) {
            ret.put("events", new JSONArray());
        }
        call.resolve(ret);
    }
'''
open(P,'w',encoding='utf-8').write(s[:i]+add+s[i:])
print('patch ok')
