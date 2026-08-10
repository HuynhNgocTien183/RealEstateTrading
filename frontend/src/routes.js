import Home from './pages/Home.svelte';
import Login from './pages/Login.svelte';
import Register from './pages/Register.svelte';
import ListingDetail from './pages/ListingDetail.svelte';
import MyListing from './pages/MyListing.svelte';
import CreateListing from './pages/CreateListing.svelte';
import AdminReview from './pages/AdminReview.svelte';
import Profile from './pages/Profile.svelte';
import SavedListings from './pages/SavedListings.svelte';

export default {
  '/': Home,
  '/login': Login,
  '/register': Register,
  '/listings/:id': ListingDetail,
  '/my-listings': MyListing,
  '/create-listing': CreateListing,
  '/admin/review': AdminReview,
  '/profile': Profile,
  '/saved-listings': SavedListings,
};