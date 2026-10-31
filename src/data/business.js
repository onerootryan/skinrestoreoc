// Single source of truth. Change it here, it changes everywhere — including schema.

export const business = {
  name: 'Skin Restore',
  legalName: 'Skin Restore',
  practitioner: 'Demi Broughton',
  tagline: 'Being comfortable in your own skin',
  credential: 'Licensed Esthetician',
  licenseNumber: 'Z91680',
  licenseBoard: 'California Board of Barbering and Cosmetology',
  yearsExperience: '15+',
  founded: '2020',
  phone: '(949) 545-7919',
  phoneHref: 'tel:+19495457919',
  email: '', // TODO: add if you want it public
  street: '312 Avenida de la Estrella',
  city: 'San Clemente',
  region: 'CA',
  postal: '92672',
  country: 'US',
  // From the map pin in your Square booking profile
  lat: 33.429081,
  lng: -117.6136729,
  priceRange: '$$$',
  areasServed: [
    'San Clemente',
    'Dana Point',
    'San Juan Capistrano',
    'Laguna Niguel',
    'Orange County',
  ],
  // Standalone Square Appointments booking flow — lives on Square's domain,
  // so it keeps working after skinrestoreoc.com moves to Netlify.
  bookingUrl: 'https://book.squareup.com/appointments/iqeoshu0dfmonc/location/LRDN4QX13C2V0/services',
  // Flip to true when Skin Restore RX launches — restores the Shop link in the
  // nav, the footer, and the homepage product section, all at once.
  // Keep false until the Online Store password is removed (target Nov 16, 2026),
  // or visitors land on a password page.
  shopLive: false,
  shopUrl: 'https://www.skinrestorerx.com/?utm_source=skinrestoreoc&utm_medium=referral',
  // Deep links for the homepage product section: each goes straight to the
  // matching Skin Restore RX page. No prices on this site — RX shows them.
  shopLinks: {
    concerns: [
      { label: 'Barrier repair', path: '/collections/barrier-repair' },
      { label: 'Breakouts & congestion', path: '/collections/acne' },
      { label: 'Uneven tone', path: '/collections/hyperpigmentation' },
      { label: 'Sensitivity', path: '/collections/sensitive-skin' },
      { label: 'Mature skin', path: '/collections/mature-skin' },
      { label: 'Post-procedure', path: '/collections/post-procedure' },
    ],
    brands: [
      { label: 'iS Clinical', path: '/collections/is-clinical' },
      { label: 'Face Reality', path: '/collections/face-reality' },
      { label: 'Hydrinity', path: '/collections/hydrinity' },
      { label: 'CO2Lift', path: '/collections/co2lift' },
      { label: 'GlyMed Plus', path: '/collections/glymed-plus' },
      { label: 'SIV', path: '/collections/siv' },
      { label: 'Ecologica', path: '/collections/ecologica' },
    ],
  },
  // Identifiable people appear on the site.
  //   Chemical Peels — a client; written consent confirmed by Demi, 22 Sep 2026.
  //   Teen Facial — licensed stock; model release covers use (confirmed 24 Sep 2026).
  //   All other treatment photos are manufacturer/licensed material.
  clientPhotoConsent: true,

  appointmentOnly: true,
  hoursNote: 'By appointment only',
  hours: [
    { days: ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], open: '10:00', close: '18:00' },
  ],
  hoursDisplay: 'Tuesday – Saturday, 10am – 6pm',
  hoursFull: 'By appointment only · Tuesday – Saturday, 10am – 6pm',
  social: {
    google: '', // TODO: Google Business Profile URL
    instagram: 'https://www.instagram.com/skinrestoreoc/',
    facebook: 'https://www.facebook.com/skinrestoreoc/',
    yelp: '',
  },
};

export const siteUrl = 'https://www.skinrestoreoc.com';
