package com.capacitorjs.plugins.localnotifications;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import androidx.core.app.NotificationManagerCompat;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Boutons « Pris » / « Ignoré » / « Fait » : traités en arrière-plan, sans ouvrir l'appli.
 * L'évènement est mémorisé ; l'appli l'applique à sa prochaine ouverture.
 */
public class QuickActionReceiver extends BroadcastReceiver {

    public static final String PREFS = "melimelo_quick";

    @Override
    public void onReceive(Context context, Intent intent) {
        try {
            int id = intent.getIntExtra(LocalNotificationManager.NOTIFICATION_INTENT_KEY, Integer.MIN_VALUE);
            String action = intent.getStringExtra(LocalNotificationManager.ACTION_INTENT_KEY);
            String src = intent.getStringExtra(LocalNotificationManager.NOTIFICATION_OBJ_INTENT_KEY);
            SharedPreferences sp = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
            JSONArray arr;
            try {
                arr = new JSONArray(sp.getString("events", "[]"));
            } catch (Exception e) {
                arr = new JSONArray();
            }
            JSONObject ev = new JSONObject();
            ev.put("action", action);
            ev.put("ts", System.currentTimeMillis());
            ev.put("id", id);
            try {
                JSONObject n = new JSONObject(src);
                JSONObject extra = n.optJSONObject("extra");
                if (extra != null) {
                    ev.put("extra", extra);
                }
            } catch (Exception e) {
                // pas d'extra
            }
            arr.put(ev);
            sp.edit().putString("events", arr.toString()).apply();
            if (id != Integer.MIN_VALUE) {
                NotificationManagerCompat.from(context).cancel(id);
            }
        } catch (Exception e) {
            // ne jamais planter en arrière-plan
        }
    }
}
