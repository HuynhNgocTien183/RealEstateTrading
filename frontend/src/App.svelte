<script>
  import { Router, Route } from 'svelte-routing';
  import Navbar from './lib/components/Navbar.svelte';
  import Home from './pages/Home.svelte';
  import Login from './pages/Login.svelte';
  import Register from './pages/Register.svelte';
  import ListingDetail from './pages/ListingDetail.svelte';
  import MyListing from './pages/MyListing.svelte';
  import CreateListing from './pages/CreateListing.svelte';
  import AdminReview from './pages/AdminReview.svelte';

  export let url = '';
</script>

<Router {url}>
  <Navbar />
  <main>
    <Route path="/" component={Home} />
    <Route path="/login" component={Login} />
    <Route path="/register" component={Register} />
    <Route path="/listings/:id" component={ListingDetail} />
    <Route path="/my-listings" component={MyListing} />
    <Route path="/create-listing" component={CreateListing} />
    <Route path="/admin/review" component={AdminReview} />
  </main>
</Router>

<style>
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
</style>