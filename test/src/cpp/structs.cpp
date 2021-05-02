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

    namespace InnerNamespace
    {
        typedef struct StructD {
            char a[100];
        } StructD;
    }
}

typedef struct StructE {
    StructA a;
    StructB b;
} StructE;

StructA struct_a;
StructB struct_b;
Namespace::StructC struct_c;
Namespace::InnerNamespace::StructD struct_d;
StructE struct_e;