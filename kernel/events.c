#include "events.h"

#define EVENT_CAP 64

static event_type_t evq[EVENT_CAP];
static int eh, et, ec;

void event_system_init(void) {
    eh = et = ec = 0;
}

void event_push(event_type_t ev) {
    if (ec >= EVENT_CAP) return;
    evq[et] = ev;
    et = (et + 1) % EVENT_CAP;
    ec++;
}

event_type_t event_poll(void) {
    if (!ec) return EVT_NONE;
    event_type_t ev = evq[eh];
    eh = (eh + 1) % EVENT_CAP;
    ec--;
    return ev;
}
