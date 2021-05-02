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

typedef struct StructF {
    StructA a[10];
} StructF;

typedef struct StructG {
    Namespace::StructC a;
} StructG;

typedef struct StructH {
    Namespace::StructC a[10];
} StructH;

namespace Namespace
{
    typedef struct StructI {
        Namespace::InnerNamespace::StructD a;
    } StructI;

    typedef struct StructJ {
        Namespace::InnerNamespace::StructD a[2];
    } StructJ;
}

StructA struct_a;
StructB struct_b;
Namespace::StructC struct_c;
Namespace::InnerNamespace::StructD struct_d;
StructE struct_e;
StructF struct_f;
StructG struct_g;
StructH struct_h;
Namespace::StructI struct_i;
Namespace::StructJ struct_j;