import { 
    Heart, Users, Stethoscope, GraduationCap, Building, 
    FlaskConical, Briefcase, Shield, Smartphone, Store,
    Building2, UserX
} from '@lucide/svelte';

// Institution to icon mapping
export const institutionIcons = {
    'friend': Heart,
    'relative': Users, 
    'medical': Stethoscope,
    'school': GraduationCap,
    'employer': Building,
    'researcher': FlaskConical,
    'worker': Briefcase,
    'police': Shield,
    'social_media_platform': Smartphone,
    'company_customer': Store,
    'company_not_customer': Building2,
    'acquaintance': Users,
    'neighbor': Users,
    'government': Building,
    'non_profit': Heart,
    'financial': Building2,
    'stranger': UserX
};