typedef struct StructA {
    char a;
    int b;
} StructA;

typedef struct StructB {
    char a[100];
} StructB;

namespace Namespace
{
    typedef struct StructC {
        char a;
        int b;
    } StructC;
}

StructA struct_a;
StructB struct_b;
Namespace::StructC struct_c;