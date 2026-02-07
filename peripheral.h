#pragma once

#include <string>

// Tüm çevre birimleri için ortak arayüz.
// Yeni donanım modülleri bu sınıftan türetilerek sisteme eklenebilir.
class Peripheral {
public:
    virtual ~Peripheral() = default;

    // Çevre biriminin insan-okunur adı.
    virtual const char* Name() const = 0;

    // Emülatör reset olduğunda çağrılır.
    virtual void Reset() = 0;

    // Her CPU adımından sonra çağrılır (gerekliyse no-op bırakılabilir).
    virtual void Tick() = 0;
};
